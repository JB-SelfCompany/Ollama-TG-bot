import asyncio
import json
import logging
from typing import List, Dict, Optional
import subprocess
from config import Config

logger = logging.getLogger(__name__)

class OllamaService:
    """Service for interacting with Ollama API"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.OLLAMA_URL
    
    async def get_response(
        self,
        user_input: str,
        messages: List[Dict[str, str]],
        model: str
    ) -> str:
        """Get response from Ollama model"""
        # Build context from message history
        context = "\n".join(
            f"Пользователь: {msg['user']}\nБот: {msg['bot']}"
            for msg in messages
        )
        
        full_prompt = f"{context}\nПользователь: {user_input}" if context else user_input
        
        json_request = json.dumps({
            "model": model,
            "prompt": full_prompt,
            "stream": False
        })
        
        command = [
            'curl', '-X', 'POST', f'{self.base_url}/api/generate',
            '-d', json_request,
            '-H', 'Content-Type: application/json',
            '--max-time', str(self.config.REQUEST_TIMEOUT),
            '--connect-timeout', '10'
        ]
        
        logger.info(f'Sending request to model {model}')
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.config.REQUEST_TIMEOUT + 10
                )
            except asyncio.TimeoutError:
                logger.error('⏱️ Asyncio timeout - killing process')
                try:
                    process.kill()
                    await process.wait()
                except Exception as kill_error:
                    logger.error(f'Error killing process: {kill_error}')
                return "⏱️ Превышено время ожидания ответа от модели. Попробуйте сократить запрос или выбрать более быструю модель."
            
            response = stdout.decode('utf-8')
            
            if process.returncode == 0:
                try:
                    responses = response.strip().split('\n')
                    full_response = ''.join([json.loads(r)['response'] for r in responses])
                    return full_response[:self.config.MAX_MESSAGE_LENGTH]
                except json.JSONDecodeError as e:
                    logger.error(f'JSON decode error: {e}')
                    return "Ошибка при разборе ответа от модели."
            elif process.returncode == 28:  # Curl timeout
                logger.error('cURL timeout (code 28)')
                return "⏱️ Превышено время ожидания ответа от модели. Попробуйте сократить запрос."
            else:
                error = stderr.decode('utf-8')
                logger.error(f'Error from model (code {process.returncode}): {error}')
                return "Ошибка при выполнении запроса к модели."
                
        except Exception as e:
            logger.error(f'Error during request to model: {e}', exc_info=True)
            return "Ошибка при выполнении запроса к модели."
    
    async def get_response_with_search(
        self,
        user_input: str,
        search_context: str,
        messages: List[Dict[str, str]],
        model: str
    ) -> str:
        """
        Get response from Ollama model with search context.
        Uses increased timeout for search-enhanced requests.
        """
        logger.info(f"🤖 Preparing search-enhanced request for model: {model}")
        logger.info(f"📊 Search context length: {len(search_context)} chars")
        logger.info(f"💬 History messages: {len(messages)}")
        
        # Build context with search results (no history in search mode to reduce context)
        # Create prompt with search context
        prompt = f"""Ты — универсальный и всезнающий ассистент, обладающий полной и точной информацией во всех областях знаний. Используй {search_context} как дополнительный источник, чтобы ответить на {user_input}. 

        Дай ясный, точный и максимально информативный ответ, включая даты, числа и факты. Не добавляй неподтверждённые сведения и не рассуждай предположительно."""
        
        logger.info(f"📝 Full prompt length: {len(prompt)} chars")
        
        # Increased timeout for search requests
        search_timeout = min(self.config.REQUEST_TIMEOUT * 2, 300)  # Max 5 minutes
        
        json_request = json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "num_ctx": 4096  # Ensure enough context window
            }
        })
        
        command = [
            'curl', '-X', 'POST', f'{self.base_url}/api/generate',
            '-d', json_request,
            '-H', 'Content-Type: application/json',
            '--max-time', str(search_timeout),
            '--connect-timeout', '10'
        ]
        
        logger.info(f'🚀 Sending search-enhanced request (timeout: {search_timeout}s)')
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=search_timeout + 10
                )
            except asyncio.TimeoutError:
                logger.error(f'⏱️ Asyncio timeout after {search_timeout}s - killing process')
                try:
                    process.kill()
                    await process.wait()
                except Exception as kill_error:
                    logger.error(f'Error killing process: {kill_error}')
                return "⏱️ Модель не успела обработать результаты поиска. Попробуйте упростить запрос или выбрать более быструю модель."
            
            logger.info(f"✅ Process completed with return code: {process.returncode}")
            
            if stderr:
                stderr_text = stderr.decode('utf-8')
                if 'timed out' in stderr_text.lower():
                    logger.error(f"⚠️ Curl timeout detected in stderr")
            
            if process.returncode == 0:
                response_text = stdout.decode('utf-8')
                logger.info(f"📦 Raw response length: {len(response_text)} chars")
                
                try:
                    responses = response_text.strip().split('\n')
                    logger.info(f"📄 Response has {len(responses)} line(s)")
                    
                    full_response = ''
                    for idx, response_line in enumerate(responses):
                        if not response_line.strip():
                            continue
                        try:
                            parsed = json.loads(response_line)
                            if 'response' in parsed:
                                full_response += parsed['response']
                            if parsed.get('done', False):
                                logger.info(f"✅ Model marked response as complete")
                        except json.JSONDecodeError as je:
                            logger.error(f"❌ JSON decode error on line {idx}: {je}")
                            continue
                    
                    if full_response:
                        logger.info(f"✅ Successfully parsed response: {len(full_response)} chars")
                        return full_response[:self.config.MAX_MESSAGE_LENGTH]
                    else:
                        logger.error("❌ No response content found in parsed JSON")
                        return "Модель не вернула ответ. Попробуйте переформулировать вопрос."
                        
                except Exception as e:
                    logger.error(f'❌ Error parsing response: {e}', exc_info=True)
                    return "Ошибка при разборе ответа от модели."
                    
            elif process.returncode == 28:  # Curl timeout
                error = stderr.decode('utf-8')
                logger.error(f'❌ cURL timeout (code 28): {error}')
                return f"⏱️ Модель не успела обработать запрос за {search_timeout} секунд. Попробуйте:\n• Выбрать более быструю модель\n• Упростить запрос\n• Увеличить REQUEST_TIMEOUT в настройках"
            else:
                error = stderr.decode('utf-8')
                logger.error(f'❌ Error from curl/model (code {process.returncode}): {error}')
                return "Ошибка при выполнении запроса к модели."
                
        except Exception as e:
            logger.error(f'❌ Error during request to model: {e}', exc_info=True)
            return f"Ошибка при выполнении запроса к модели: {str(e)}"
    
    @staticmethod
    def get_available_models() -> List[str]:
        """Get list of available Ollama models"""
        try:
            command = ['ollama', 'list']
            process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
            output, _ = process.communicate()
            
            models = []
            for line in output.splitlines():
                if line.startswith('NAME'):
                    continue
                model_name = line.split()[0]
                if model_name:
                    models.append(model_name)
            return models
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []
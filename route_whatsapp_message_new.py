async def route_whatsapp_message_new(sender: str, text: str, message_id: str = None) -> str:
    """Route WhatsApp message with proper user detection and onboarding (mirrors Telegram)"""
    try:
        logger.info(f"📱 WhatsApp message from {sender}: '{text}'")
        
        # Import APIs
        from utils.whatsapp_api_fixed import whatsapp_api
        from utils.whatsapp_onboarding_manager import whatsapp_onboarding
        
        # 🎯 STEP 1: User lookup and onboarding check (like Telegram)
        # Create payload structure for the onboarding manager
        webhook_payload = {
            'entry': [{
                'changes': [{
                    'value': {
                        'messages': [{
                            'from': sender,
                            'type': 'text',
                            'text': {'body': text}
                        }]
                    }
                }]
            }]
        }
        
        # Check if user needs onboarding
        onboarding_result = await whatsapp_onboarding.handle_whatsapp_incoming(webhook_payload)
        
        # 🚀 STEP 2: Handle onboarding vs normal flow
        if onboarding_result.get('onboarding_needed'):
            logger.info(f"🆕 User {sender} needs onboarding - sending interactive button")
            
            # Send interactive button message
            if onboarding_result.get('button_data'):
                success = await whatsapp_api.send_interactive_button_message(
                    phone_number=sender,
                    interactive_data=onboarding_result['button_data']['interactive']
                )
                
                if success:
                    return "Onboarding flow sent with interactive button"
                else:
                    # Fallback to plain text
                    fallback_msg = onboarding_result.get('message', 'Welcome! Please complete registration.')
                    await whatsapp_api.send_message_with_read_and_typing(
                        phone_number=sender,
                        message=fallback_msg,
                        message_id_to_read=message_id,
                        typing_duration=1.0
                    )
                    return "Onboarding flow sent (fallback)"
            
        elif onboarding_result.get('proceed_to_assistant'):
            logger.info(f"✅ User {sender} is onboarded - proceeding to Assistant")
            
            # 🤖 STEP 3: Process via Sofi Assistant API (existing users)
            from utils.sofi_assistant_api import sofi_assistant
            
            # Send message to Sofi Assistant and get intelligent response
            assistant_response = await sofi_assistant.send_message_to_assistant(sender, text)
            
            if assistant_response:
                logger.info(f"✅ Sofi Assistant response generated for {sender}")
                
                # Send with proper Meta API typing indicator
                success = await whatsapp_api.send_message_with_read_and_typing(
                    phone_number=sender,
                    message=assistant_response,
                    message_id_to_read=message_id,
                    typing_duration=2.0
                )
                
                return "Message processed by Sofi Assistant"
            else:
                logger.error(f"❌ Assistant failed for {sender}")
                
                # Send error message
                await whatsapp_api.send_message_with_read_and_typing(
                    phone_number=sender,
                    message="Sorry, I'm having trouble right now. Please try again in a moment.",
                    message_id_to_read=message_id,
                    typing_duration=1.0
                )
                
                return "Assistant error - fallback sent"
        
        else:
            # Something went wrong with onboarding check
            logger.error(f"❌ Onboarding check failed for {sender}")
            
            await whatsapp_api.send_message_with_read_and_typing(
                phone_number=sender,
                message="Sorry, I'm experiencing technical difficulties. Please try again later.",
                message_id_to_read=message_id,
                typing_duration=1.0
            )
            
            return "Onboarding check failed"
            
    except Exception as e:
        logger.error(f"❌ Error routing WhatsApp message: {e}")
        
        # Emergency fallback
        try:
            from utils.whatsapp_api_fixed import whatsapp_api
            await whatsapp_api.send_message_with_read_and_typing(
                phone_number=sender,
                message="I'm experiencing technical difficulties. Please try again in a few minutes.",
                message_id_to_read=message_id,
                typing_duration=1.0
            )
        except:
            pass
            
        return f"Error: {str(e)}"

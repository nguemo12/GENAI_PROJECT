import axios from 'axios';
import { MessageInterface } from '@/types/types';
import { API_KEY } from '@/config/runpodConfigs';

async function callChatBotAPI(messages: MessageInterface[]): Promise<MessageInterface> {
    try {
        const response = await axios.post( {
            input: { messages }
        }, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${API_KEY}`
            }
        });
        
        let output = response.data;
        let outputMessage: MessageInterface = output['output'];

        return outputMessage;
    } catch (error) {
        console.error('Error calling the API:', error);
        throw error;
    }
}

export { callChatBotAPI };
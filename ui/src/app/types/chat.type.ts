export enum RoleType {
    USER = 'user',
    ASSISTANT = 'assistant',
}

export interface CommandModel {
    name: string;
    arguments: object;
    result: string;
    cache_hit: boolean;
}

export interface MessageModel {
    id: string;
    role: RoleType;
    text: string | null;
    reasoning: string | null;
    command: string | null;
}

export enum LLMType {
    GEMINI = 'gemini',
    DEEPSEEK = 'deepseek',
}

export interface ChatModel {
    id: string | null;
    llm_type: LLMType;
    title: string | null;
    messages: MessageModel[];
}

export interface ChatIdModel {
    id: string;
}

export interface ChatReducedModel {
    id: string;
    llm_type: LLMType;
    title: string | null;
}

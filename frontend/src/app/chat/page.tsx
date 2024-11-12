"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Send } from "lucide-react";
import { askQuestion } from "@/lib/api";

interface Message {
    sender: "user" | "assistant";
    text: string;
}

export default function Chat() {
    const [question, setQuestion] = React.useState("");
    const [messages, setMessages] = React.useState<Message[]>([]);
    const [isLoading, setIsLoading] = React.useState(false);
    const messagesEndRef = React.useRef<HTMLDivElement>(null);

    React.useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const handleQuestionSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        if (!question.trim()) return;

        setMessages((prevMessages) => [
            ...prevMessages,
            { sender: "user", text: question },
        ]);
        setQuestion("");
        setIsLoading(true);

        try {
            const response = await askQuestion(question);
            const assistantAnswer = response.answer;

            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "assistant", text: assistantAnswer },
            ]);
        } catch (error) {
            console.error("Error:", error);
            setMessages((prevMessages) => [
                ...prevMessages,
                {
                    sender: "assistant",
                    text: "Sorry, there was an error processing your question.",
                },
            ]);
        }

        setIsLoading(false);
    };

    return (
        <Card className="max-w-2xl mx-auto mt-8 border border-gray-200 shadow-lg">
            <CardContent className="p-0">
                <ScrollArea className="h-[calc(100vh-200px)] p-4">
                    {messages.map((message, index) => (
                        <div key={index} className="flex mb-4 items-start">
                            {message.sender === "assistant" && (
                                <Avatar className="h-8 w-8 mr-3">
                                    <AvatarImage
                                        src="/placeholder.svg?height=32&width=32"
                                        alt="AI Assistant"
                                    />
                                    <AvatarFallback>AI</AvatarFallback>
                                </Avatar>
                            )}
                            <div
                                className={`rounded-lg p-3 max-w-[80%] ${
                                    message.sender === "user"
                                        ? "bg-gray-100 text-gray-800 ml-auto"
                                        : "bg-white border border-gray-200 text-gray-800"
                                }`}
                            >
                                {message.text}
                            </div>
                            {message.sender === "user" && (
                                <Avatar className="h-8 w-8 ml-3">
                                    <AvatarImage
                                        src="/placeholder.svg?height=32&width=32"
                                        alt="User"
                                    />
                                    <AvatarFallback>U</AvatarFallback>
                                </Avatar>
                            )}
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </ScrollArea>
                <div className="border-t border-gray-200 p-4">
                    <form
                        onSubmit={handleQuestionSubmit}
                        className="flex items-center space-x-2"
                    >
                        <Input
                            type="text"
                            placeholder="Type your message..."
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            className="flex-grow"
                            disabled={isLoading}
                        />
                        <Button
                            type="submit"
                            disabled={!question.trim() || isLoading}
                            variant="outline"
                        >
                            <Send className="h-4 w-4" />
                            <span className="sr-only">Send</span>
                        </Button>
                    </form>
                </div>
            </CardContent>
        </Card>
    );
}

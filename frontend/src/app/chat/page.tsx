"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Send } from "lucide-react";

export default function Chat() {
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const handleQuestionSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setIsLoading(true);
        try {
            const response = await fetch("http://localhost:8000/ask", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ question }),
            });
            const data = await response.json();
            setAnswer(data.answer);
        } catch (error) {
            console.error("Error:", error);
            setAnswer("Sorry, there was an error processing your question.");
        }
        setIsLoading(false);
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Ask a Question</CardTitle>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleQuestionSubmit} className="space-y-4">
                    <Textarea
                        placeholder="Enter your question here..."
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        className="w-full"
                    />
                    <Button
                        type="submit"
                        disabled={!question.trim() || isLoading}
                    >
                        <Send className="mr-2 h-4 w-4" />
                        {isLoading ? "Processing..." : "Submit Question"}
                    </Button>
                </form>
                {answer && (
                    <div className="mt-4 p-4 bg-secondary rounded-lg">
                        <h3 className="font-semibold mb-2">Answer:</h3>
                        <p>{answer}</p>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

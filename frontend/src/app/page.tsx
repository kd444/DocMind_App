"use client";

import { useState, useRef } from "react";
import { Upload, Send, FileText, Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const Logo = () => (
    <div className="flex items-center space-x-2">
        <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="h-6 w-6 text-primary"
        >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
        </svg>
        <span className="font-bold text-xl">DocMind</span>
    </div>
);

const Navbar = () => (
    <nav className="bg-background border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
                <Logo />
                <div className="hidden md:block">
                    <div className="ml-10 flex items-baseline space-x-4">
                        <a
                            href="#"
                            className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                        >
                            Home
                        </a>
                        <a
                            href="#"
                            className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                        >
                            About
                        </a>
                        <a
                            href="#"
                            className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                        >
                            Contact
                        </a>
                    </div>
                </div>
                <div className="md:hidden">
                    <Button variant="ghost" size="icon">
                        <Menu className="h-6 w-6" />
                    </Button>
                </div>
            </div>
        </div>
    </nav>
);

export default function DocMind() {
    const [file, setFile] = useState<File | null>(null);
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            setFile(event.target.files[0]);
        }
    };

    const handleUpload = () => {
        if (file) {
            // Here you would typically send the file to your backend
            console.log("Uploading file:", file.name);
            // Reset file input
            if (fileInputRef.current) {
                fileInputRef.current.value = "";
            }
            setFile(null);
        }
    };

    const handleQuestionSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        // Here you would typically send the question to your backend
        console.log("Submitting question:", question);
        // Simulate an answer
        setAnswer(`This is a simulated answer to your question: "${question}"`);
        setQuestion("");
    };

    return (
        <div className="min-h-screen bg-background text-foreground">
            <Navbar />
            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div className="px-4 py-6 sm:px-0">
                    <Card className="mb-6">
                        <CardHeader>
                            <CardTitle>Upload Document</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-center space-x-2">
                                <Input
                                    type="file"
                                    onChange={handleFileChange}
                                    ref={fileInputRef}
                                    className="flex-grow"
                                />
                                <Button onClick={handleUpload} disabled={!file}>
                                    <Upload className="mr-2 h-4 w-4" /> Upload
                                </Button>
                            </div>
                            {file && (
                                <p className="mt-2 text-sm text-gray-500">
                                    <FileText className="inline mr-1 h-4 w-4" />
                                    {file.name}
                                </p>
                            )}
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader>
                            <CardTitle>Ask a Question</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <form
                                onSubmit={handleQuestionSubmit}
                                className="space-y-4"
                            >
                                <Textarea
                                    placeholder="Enter your question here..."
                                    value={question}
                                    onChange={(e) =>
                                        setQuestion(e.target.value)
                                    }
                                    className="w-full"
                                />
                                <Button
                                    type="submit"
                                    disabled={!question.trim()}
                                >
                                    <Send className="mr-2 h-4 w-4" /> Submit
                                    Question
                                </Button>
                            </form>
                            {answer && (
                                <div className="mt-4 p-4 bg-secondary rounded-lg">
                                    <h3 className="font-semibold mb-2">
                                        Answer:
                                    </h3>
                                    <p>{answer}</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </main>
        </div>
    );
}

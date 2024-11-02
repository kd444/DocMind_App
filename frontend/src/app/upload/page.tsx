"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload, FileText } from "lucide-react";

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            setFile(event.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (file) {
            setIsUploading(true);
            const formData = new FormData();
            formData.append("file", file);

            try {
                const response = await fetch("http://localhost:8000/upload", {
                    method: "POST",
                    body: formData,
                });
                const data = await response.json();
                console.log("Upload successful:", data);
                // Reset file input
                if (fileInputRef.current) {
                    fileInputRef.current.value = "";
                }
                setFile(null);
            } catch (error) {
                console.error("Upload error:", error);
            }

            setIsUploading(false);
        }
    };

    return (
        <Card>
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
                    <Button
                        onClick={handleUpload}
                        disabled={!file || isUploading}
                    >
                        <Upload className="mr-2 h-4 w-4" />
                        {isUploading ? "Uploading..." : "Upload"}
                    </Button>
                </div>
                {file && (
                    <p className="mt-2 text-sm text-muted-foreground">
                        <FileText className="inline mr-1 h-4 w-4" />
                        {file.name}
                    </p>
                )}
            </CardContent>
        </Card>
    );
}

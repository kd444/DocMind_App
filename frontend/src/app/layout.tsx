import { Inter } from "next/font/google";
import { Sidebar } from "@/components/sidebar";
import { Header } from "@/components/header";
import "@/app/globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
    title: "DocMind",
    description: "Document Management and Q&A Platform",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <div className="flex h-screen bg-background">
                    <Sidebar />
                    <div className="flex flex-col flex-1 overflow-hidden">
                        <Header />
                        <main className="flex-1 overflow-y-auto p-4">
                            {children}
                        </main>
                    </div>
                </div>
            </body>
        </html>
    );
}

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, MessageSquare, Upload } from "lucide-react";
import { cn } from "@/lib/utils";

export function Sidebar() {
    const pathname = usePathname();

    const links = [
        { href: "/", label: "Home", icon: Home },
        { href: "/chat", label: "Chat", icon: MessageSquare },
        { href: "/upload", label: "Upload", icon: Upload },
    ];

    return (
        <div className="w-64 bg-secondary text-secondary-foreground p-4">
            <div className="flex items-center mb-8">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-8 w-8 mr-2 text-primary"
                >
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="16" y1="13" x2="8" y2="13" />
                    <line x1="16" y1="17" x2="8" y2="17" />
                    <polyline points="10 9 9 9 8 9" />
                </svg>
                <span className="font-bold text-2xl">DocMind</span>
            </div>
            <nav>
                <ul className="space-y-2">
                    {links.map((link) => (
                        <li key={link.href}>
                            <Link
                                href={link.href}
                                className={cn(
                                    "flex items-center p-2 rounded-lg hover:bg-primary/10",
                                    pathname === link.href &&
                                        "bg-primary/10 text-primary"
                                )}
                            >
                                <link.icon className="mr-2 h-5 w-5" />
                                {link.label}
                            </Link>
                        </li>
                    ))}
                </ul>
            </nav>
        </div>
    );
}


import { AppConfig } from "./types.js";

export const config: AppConfig = {
    key: "generic_chat",
    title: "Generic Chat",
    heroImage: "/hero.png",
    heroImageDark: "/hero-dark.png",
    background: "#f0f0f0",
    placeholder: "Try 'Tell me a joke' or 'Top 5 fruits'",
    loadingText: [
        "Thinking...",
        "Generating UI...",
    ],
    serverUrl: "http://localhost:10003",
};

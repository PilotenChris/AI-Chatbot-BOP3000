import React, { useState } from "react";

const Chatbot = () => {
    const [isOpen, setIsOpen] = useState(false);

    const toggleChatbot = () => {
        setIsOpen(!isOpen);
    };

    return (
        <>
            {!isOpen && (
                <button className="chatbot-toggle" onClick={toggleChatbot}>
                    +
                </button>
            )}
            {isOpen && (
                <div className="chatbot">
                    <div className="chatbot-header">
                        Chat with Us!
                        <button className="chatbot-close" onClick={toggleChatbot}>x</button>
                    </div>
                    <div className="chatbot-content">
                        Welcome to our chat service
                    </div>
                </div>
            )}
        </>
    );
};

export default Chatbot;
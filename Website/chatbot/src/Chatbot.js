import React, { useState, useEffect, useRef } from "react";

const Chatbot = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [isFinished, setIsFinished] = useState(false);
    const [selectedOption, setSelectedOption] = useState(null);
    const [messages, setMessages] = useState([]);
    const [email, setEmail] = useState("");
    const [feedback, setFeedback] = useState("");
    const [isFeedbackAllowed, setIsFeedbackAllowed] = useState(false);
    const initialMessageFetched = useRef(false);

    const toggleChatbot = () => {
        if (isFinished) {
            // Reset everything and close the chatbox
            setIsOpen(false);
            setIsFinished(false);
            setSelectedOption(null);
            setMessages([]);
            setEmail("");
            setFeedback("");
            setIsFeedbackAllowed(false);
        } else {
            setIsOpen(!isOpen);
        }
        
    };

    // Checks if the user has selected a type of chat before they pressed on the close button
    // If not then close the chat, else give them the finish page
    const handleSetFinish = () => {
        if (selectedOption === null) {
            setIsOpen(false);
        } else {
            setIsFinished(true);
        }
    }

    // Handle the chat type the user has selected
    const handleOptionSelect = (optionNumber) => {
        setSelectedOption(optionNumber);
    };

    // Make sure to check if the user are allowed to send feedback as soon as the chat window opens
    // Also get the greeting message from the chatbot if it's the first time the user opens the chat
    useEffect(() => {
        const checkFeedbackAllowed = async () => {
            if (isOpen) {
                try {
                    const response = await fetch("http://127.0.0.1:8000/feedback/check/", {
                    method: "GET"
                });
                    const data = await response.json();
                    setIsFeedbackAllowed(data.isFeedbackAllowed);
                } catch (error) {
                    console.error("Error checking if feedback is allowed:", error);
                    setIsFeedbackAllowed(false);
                }
            }
        };

        const fetchGreetingMessage = async () => {
            if (isOpen && !initialMessageFetched.current) {
                try {
                    const response = await fetch("http://127.0.0.1:8000/greeting/", {
                    method: "GET"
                });
                    const data = await response.json();
                    setMessages([{ text: data.greeting, from: "bot" }]);
                    initialMessageFetched.current = true;
                } catch (error) {
                    console.error("Error featching the greeting message:", error);
                }
            }
        };

        checkFeedbackAllowed();
        fetchGreetingMessage();
    }, [isOpen]);

    // Send message to the Django REST API and get a answer back
    const handleSendMessage = async (event) => {
        event.preventDefault();
        const message = event.target.elements.message.value;
        event.target.elements.message.value = "";
        if (message.trim()) {
            setMessages([...messages, { text: message, from: "user" }]);
             const url = selectedOption === 0
            ? "http://127.0.0.1:8000/information/"
            : "http://127.0.0.1:8000/complaint/";
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message, option: selectedOption })
            });

            const data = await response.json();
            setMessages(messages => [...messages, { text: data.response, from: "bot" }]);
        }
    };

    // Send the conversation with the chatbot to the users provided email
    const handleFinish = async () => {
        await fetch("YOUR_DJANGO_API_EMAIL_URL", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, messages })
        });
    };

    // Save the chat with the chatbot and the feedback from the user
    const handleFeedback = async () => {
        await fetch("http://127.0.0.1:8000/feedback/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ feedback, messages })
        });
    };

    return (
        <>
            {!isOpen && (
                <button className="chatbot-toggle" onClick={toggleChatbot}>
                    +
                </button>
            )}
            {isOpen && !isFinished && (
                <div className="chatbot">
                    <div className="chatbot-header">
                        Chatbot for forbrukere
                        <button className="chatbot-close" onClick={handleSetFinish}>x</button>
                    </div>
                    {selectedOption === null ? (
                        <div className="chatbot-options">
                            <button onClick={() => handleOptionSelect(0)}>Spørsmål om informasjon</button>
                            <button onClick={() => handleOptionSelect(1)}>Spørsmål om tips/klage saker</button>
                        </div>
                    ) : (
                        <>
                            <div className="chatbot-content">
                                {messages.map((msg, index) => (
                                    <div key={index} className={`message ${msg.from}`}>
                                        {msg.text}
                                    </div>
                                ))}
                            </div>
                            <form className="chatbot-chat" onSubmit={handleSendMessage}>
                                <input type="text" name="message" placeholder="Spørsmål..." autoComplete="off" />
                                <button type="submit">Send</button>
                            </form>
                        </>
                    )}
                </div>
            )}
            {isOpen && isFinished && (
                <div className="chatbot">
                    <div className="chatbot-header">
                        Takk for samtalen
                        <button className="chatbot-close" onClick={toggleChatbot}>x</button>
                    </div>
                    <div className="chatbot-finish">
                        <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Din e-post" autoComplete="off" />
                        <button onClick={handleFinish}>Send e-post</button>
                        {isFeedbackAllowed && (
                            <div className="feedback-section">
                                <textarea value={feedback} onChange={e => setFeedback(e.target.value)} placeholder="Din tilbakemelding" />
                                <button onClick={handleFeedback}>Send tilbakemelding</button>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </>
    );
};

export default Chatbot;
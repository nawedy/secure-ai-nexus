// Next.js Frontend Boilerplate for LLM Chatbot

import { useState } from "react";

export default function Home() {  
  const \[input, setInput\] \= useState("");  
  const \[response, setResponse\] \= useState("");  
  const \[loading, setLoading\] \= useState(false);

  const handleSubmit \= async (e) \=\> {  
    e.preventDefault();  
    setLoading(true);  
    try {  
      const res \= await fetch("/api/chat", {  
        method: "POST",  
        headers: { "Content-Type": "application/json" },  
        body: JSON.stringify({ prompt: input }),  
      });  
      const data \= await res.json();  
      setResponse(data.response);  
    } catch (error) {  
      setResponse("Error fetching response.");  
    }  
    setLoading(false);  
  };

  return (  
    \<div className="min-h-screen flex flex-col items-center justify-center p-4"\>  
      \<h1 className="text-2xl font-bold mb-4"\>AI Chatbot\</h1\>  
      \<form onSubmit={handleSubmit} className="w-full max-w-md"\>  
        \<input  
          type="text"  
          value={input}  
          onChange={(e) \=\> setInput(e.target.value)}  
          placeholder="Type a message..."  
          className="border p-2 rounded w-full"  
        /\>  
        \<button type="submit" className="bg-blue-500 text-white p-2 rounded mt-2 w-full"\>  
          {loading ? "Loading..." : "Send"}  
        \</button\>  
      \</form\>  
      {response && (  
        \<div className="mt-4 p-4 border rounded w-full max-w-md bg-gray-100"\>  
          \<p\>{response}\</p\>  
        \</div\>  
      )}  
    \</div\>  
  );  
}


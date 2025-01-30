// React Native Boilerplate for LLM Chatbot

import React, { useState } from 'react';  
import { View, Text, TextInput, Button, ActivityIndicator, StyleSheet } from 'react-native';

export default function ChatScreen() {  
  const \[input, setInput\] \= useState('');  
  const \[response, setResponse\] \= useState('');  
  const \[loading, setLoading\] \= useState(false);

  const handleSubmit \= async () \=\> {  
    setLoading(true);  
    try {  
      const res \= await fetch('https://your-api-endpoint.com/chat', {  
        method: 'POST',  
        headers: { 'Content-Type': 'application/json' },  
        body: JSON.stringify({ prompt: input }),  
      });  
      const data \= await res.json();  
      setResponse(data.response);  
    } catch (error) {  
      setResponse('Error fetching response.');  
    }  
    setLoading(false);  
  };

  return (  
    \<View style={styles.container}\>  
      \<Text style={styles.title}\>AI Chatbot\</Text\>  
      \<TextInput  
        style={styles.input}  
        value={input}  
        onChangeText={setInput}  
        placeholder="Type a message..."  
      /\>  
      \<Button title="Send" onPress={handleSubmit} disabled={loading} /\>  
      {loading && \<ActivityIndicator size="large" color="\#0000ff" /\>}  
      {response ? \<Text style={styles.response}\>{response}\</Text\> : null}  
    \</View\>  
  );  
}

const styles \= StyleSheet.create({  
  container: {  
    flex: 1,  
    justifyContent: 'center',  
    alignItems: 'center',  
    padding: 20,  
  },  
  title: {  
    fontSize: 24,  
    fontWeight: 'bold',  
    marginBottom: 20,  
  },  
  input: {  
    width: '100%',  
    borderWidth: 1,  
    padding: 10,  
    marginBottom: 10,  
    borderRadius: 5,  
  },  
  response: {  
    marginTop: 20,  
    padding: 10,  
    borderWidth: 1,  
    borderRadius: 5,  
    backgroundColor: '\#f0f0f0',  
  },  
});


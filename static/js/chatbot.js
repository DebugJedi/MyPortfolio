let file;
let upload =false;

function displayFileName() {
    
    const input = document.getElementById('file-upload');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    resetUI();
    file = input.files[0];
    if (file) {
        fileName.textContent = file.name;
        fileInfo.style.display = 'block';
    }
}

async function resetUI(){
    
    const chatHistory = document.getElementById('chat-history');
    chatHistory.innerHTML = '';
    document.getElementById("upload-message").textContent = "";
    document.getElementById("response").textContent = "";
    document.getElementById("query").value = "";
    file = null;
    document.getElementById('chat-container').style.display = 'none';
    document.getElementById('chat-history').style.display = 'none';
    
}

async function uploadFile() {
    
    document.getElementById("loading-spinner").style.display = "block"; // Show spinner
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0]; // Get the selected file

    if (!file) {
        document.getElementById("upload-message").textContent = "Please select a file to upload.";
        document.getElementById("upload-message").style.color = "red";
        return;
    }
    const formData = new FormData();
    formData.append('file', file);
    try{
    const response = await fetch('/upload_pdf', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    document.getElementById('response').textContent = result.message;
    document.getElementById("loading-spinner").style.display = "none"; // Hide spinner
    if (response.ok){
        document.getElementById("upload-message").textContent = "Successfully Uploaded";
        document.getElementById("upload-message").style.color = "green";
        upload = true;
        document.getElementById('chat-container').style.display = "block";
        document.getElementById('chat-history').style.display = "block";
    } else {
      document.getElementById("upload-message").textContent = 'Error: ${result.detail}';
      document.getElementById("upload-message").style.color = "red";
      }
} catch (error){
  document.getElementById("upload-message").textContent = "An error occured while uploading. Please try again later.";
  document.getElementById("upload-message").style.color = "red";
  }
    

} 
async function handleFileChange() {
    
  uploadFile();
  resetUI();
    
}



async function askQuestion() {
    const query = document.getElementById('query').value.trim();
    const chatHistory = document.getElementById('chat-history');

    if (!query) {
        alert("please enter a question!");
        return;
    }
    // Display user's question in chat history
    const userMessage = document.createElement('div');
    userMessage.classList.add('user-message');
    userMessage.textContent = query;
    chatHistory.appendChild(userMessage);

    // Scroll to the bottom of the chat history
    chatHistory.scrollTop = chatHistory.scrollHeight;

    try {
        // Send query to server
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Failed to get a response from the server.");
        }

        const result = await response.json();

        // Display response in chat history
        const botMessage = document.createElement('div');
        botMessage.classList.add('bot-message');
        botMessage.textContent = result.response;
        chatHistory.appendChild(botMessage);

        // Scroll to the bottom of the chat history
        chatHistory.scrollTop = chatHistory.scrollHeight;

    } catch (error) {
        const errorMessage = document.createElement('div');
        errorMessage.classList.add('error-message');
        errorMessage.textContent = `Error: ${error.message}`;
        chatHistory.appendChild(errorMessage);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // Clear the input field after the message is sent
    document.getElementById('query').value = '';
}
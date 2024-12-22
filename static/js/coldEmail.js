const submitButton = document.getElementById('submit-button');
const resumeUpload = document.getElementById('resume-upload');
const jobUrlInput = document.getElementById('job-url');
const loading = document.getElementById('loading');
const resultDiv = document.getElementById('result');

submitButton.addEventListener('click', async () => {
    const resumeFile = resumeUpload.files[0];
    const jobUrl = jobUrlInput.value;

    if (!resumeFile || !jobUrl) {
        resultDiv.innerHTML = "<p>Please fill all the necessary info.</p>";
        return;
    }

    loading.style.display = 'block';
    resultDiv.innerHTML = ''; // Clear previous results

    try {
        const formData = new FormData();
        formData.append('resume', resumeFile);
        formData.append('job_url', jobUrl);

        const response = await fetch('/generate_email', { 
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        loading.style.display = 'none';

        const emailContent = data.email
            .split('\n\n') // Split the email into paragraphs
            .map(paragraph => `<p>${paragraph.replace(/\n/g, '<br>')}</p>`) // Replace single newlines with <br>
            .join(''); // Combine all paragraphs into one string

        if (response.ok) {
            console.log("The email: ", emailContent)
            resultDiv.innerHTML = `<span class="ai generated_email">${emailContent}</span>`;
        } else {
            resultDiv.innerHTML = `<p>Error: ${data.error}</p>`;
        }
    } catch (error) {
        loading.style.display = 'none';
        resultDiv.innerHTML = `<p>An error occurred: ${error.message}</p>`;
    }
});
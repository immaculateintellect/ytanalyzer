<script setup>
import { Head, Link } from "@inertiajs/vue3";
import { ref, computed } from "vue";

const videoSrc = ref("");
const current_user = ref(null);
const videoPlayer = ref(null);

const video = computed(() => {
    const videoUrl = videoSrc.value.trim();
    if (!videoUrl) {
        return;
    }

    const videoId = extractVideoId(videoUrl);
    if (!videoId) {
        alert("Please enter a valid YouTube URL");
        return;
    }

    const embedUrl = "https://www.youtube.com/embed/" + videoId + "?rel=0";
    setTimeout(() => {
        videoPlayer.value.setAttribute("title", "YouTube video player");
        videoPlayer.value.setAttribute("frameborder", "0");
        videoPlayer.value.setAttribute(
            "allow",
            "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        );
        videoPlayer.value.setAttribute("allowfullscreen", "");
    }, 100);
    return embedUrl;
});

function extractVideoId(videoUrl) {
    const regex =
        /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/?)|youtu\.be\/)([\w-]{11})/;
    const match = videoUrl.match(regex);
    return match ? match[1] : null;
}
// const chatMessages = document.getElementById("chat-messages");
// const videoUrlInput = document.getElementById("video-url");

// document.addEventListener("DOMContentLoaded", function () {
//     const videoPlayer = document.getElementById("video-player");
//     const loadVideoButton = document.getElementById("load-video");
//     const questionInput = document.getElementById("question-input");
//     const sendQuestionButton = document.getElementById("send-question");
//     const downloadTranscriptButton = document.getElementById(
//         "download-transcript"
//     );

//     function displayMessage(message, className, isAI = false) {
//         const messageElement = document.createElement("div");
//         messageElement.classList.add(className);
//         messageElement.textContent = message;

//         if (isAI) {
//             const loadingDots = document.createElement("div");
//             loadingDots.classList.add("loading-dots");
//             loadingDots.innerHTML = "<span></span><span></span><span></span>";
//             messageElement.appendChild(loadingDots);
//         }

//         chatMessages.appendChild(messageElement);
//         chatMessages.scrollTop = chatMessages.scrollHeight;
//         return messageElement;
//     }

//     function askQuestion() {
//         const question = questionInput.value.trim();
//         if (!question) return;

//         displayMessage("You: " + question, "user-message");
//         questionInput.value = "";

//         const aiMessageElement = displayMessage("AI: ", "ai-message", true);
//         const loadingDots = aiMessageElement.querySelector(".loading-dots");
//         loadingDots.style.display = "inline-block";

//         fetch("/ask", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json",
//             },
//             body: JSON.stringify({
//                 video_url: videoUrlInput.value.trim(),
//                 question: question,
//             }),
//         })
//             .then((response) => response.json())
//             .then((data) => {
//                 const answer = data.answer;
//                 aiMessageElement.textContent = "AI: " + answer;
//             })
//             .catch((error) => {
//                 console.error("Error:", error);
//             })
//             .finally(() => {
//                 loadingDots.style.display = "none";
//             });
//     }

function loadVideo() {}

//     function downloadTranscript() {
//         let transcript = "";
//         chatMessages
//             .querySelectorAll(".user-message, .ai-message")
//             .forEach((messageElement) => {
//                 transcript += messageElement.textContent + "\n";
//             });
//         transcript += "\n" + "YouTube Video URL: " + videoUrlInput.value.trim();

//         const currentDate = new Date();
//         const formattedDate = currentDate.toISOString().slice(0, 10);

//         const blob = new Blob([transcript], {
//             type: "text/plain;charset=utf-8",
//         });
//         const url = URL.createObjectURL(blob);
//         const link = document.createElement("a");
//         link.href = url;
//         link.download = "TubeAsk_Transcript_" + formattedDate + ".txt";
//         link.click();
//         URL.revokeObjectURL(url);
//     }

//     loadVideoButton.addEventListener("click", loadVideo);
//     sendQuestionButton.addEventListener("click", askQuestion);
//     downloadTranscriptButton.addEventListener("click", downloadTranscript);
//     questionInput.addEventListener("keydown", function (event) {
//         if (event.key === "Enter") {
//             askQuestion();
//         }
//     });
//     videoUrlInput.addEventListener("keydown", function (event) {
//         if (event.key === "Enter") {
//             loadVideo();
//         }
//     });
// });

// const instructionsModal = document.getElementById("instructions-modal");
// const instructionsButton = document.getElementById("instructions-button");
// const closeButton = document.querySelector(".close");

// instructionsButton.addEventListener("click", function () {
//     instructionsModal.classList.toggle("hidden");
//     if (!instructionsModal.classList.contains("hidden")) {
//         instructionsModal.classList.add("show");
//     } else {
//         instructionsModal.classList.remove("show");
//     }
// });

// closeButton.addEventListener("click", function () {
//     instructionsModal.classList.toggle("hidden");
//     if (!instructionsModal.classList.contains("hidden")) {
//         instructionsModal.classList.add("show");
//     } else {
//         instructionsModal.classList.remove("show");
//     }
// });

function toggleInstructions() {}
// window.addEventListener("click", function (event) {
//     if (event.target == instructionsModal) {
//         instructionsModal.classList.toggle("hidden");
//         if (!instructionsModal.classList.contains("hidden")) {
//             instructionsModal.classList.add("show");
//         } else {
//             instructionsModal.classList.remove("show");
//         }
//     }
// });
</script>

<template>
    <Head title="TubeAsk" />
    <div class="flex justify-between">
        <div>
            <div
                id="instructions-button"
                class="rounded-md cursor-pointer text-bold m-2 py-1 px-2 hover:bg-[#f4f4f4] bg-[#ffe0d1] text-[#ff581a] shadow-md"
            >
                Instructions
            </div>
        </div>
        <div>
            <div v-if="current_user?.is_authenticated">
                <p class="user-info">Hello, {{ current_user.name }}!</p>
                <a
                    class="rounded-xl cursor-pointer text-bold m-2 py-1 px-2 hover:bg-[#f4f4f4] bg-[#ffe0d1] text-[#ff581a] shadow-md"
                    href="/logout"
                    >Logout</a
                >
            </div>
            <div
                class="rounded-md cursor-pointer text-bold m-2 p-1 hover:bg-[#f4f4f4] bg-[#ffe0d1] text-[#ff581a] shadow-md"
            >
                <a class="w-full h-full" href="/login"> Login with Google </a>
            </div>
        </div>
    </div>

    <!-- <div id="instructions-modal">
            <div class="instructions-modal-content">
                <span class="close">&times;</span>
                <div class="text-container">
                    <p>
                        1. Obtain your YouTube video or YouTube Short video URL
                        link.
                    </p>
                    <p>
                        2. Enter your URL link into the "Enter Your YouTube
                        URL..." box.
                    </p>
                    <p>3. Click "Load Video".</p>
                    <p>4. After the video loads, proceed to the chat box.</p>
                    <p>5. Type your question you'd like the AI to answer.</p>
                    <p>6. Click "Send".</p>
                    <p>
                        7. Wait for the AI to process your question and provide
                        a response.
                    </p>
                    <br />
                    <p>
                        If your video is longer than 10 minutes, you'll need to
                        subscribe to our premium service.
                    </p>
                </div>
            </div>
        </div>
         -->
    <div
        class="max-w-[600px] bg-[#ffe0d1] p-2 rounded-md my-auto mx-auto"
        style="
            box-shadow: 0 12px 16px rgba(0, 0, 0, 0.24),
                0 10px 14px rgba(0, 0, 0, 0.24);
        "
    >
        <h1 class="text-2xl text-center">TubeAsk</h1>
        <h2 class="subtitle text-center">Summarize YouTube Videos Using AI</h2>

        <div class="p-2 rounded-lg">
            <iframe
                ref="videoPlayer"
                id="video-player"
                :src="video"
                frameborder="0"
                allowfullscreen
                class="w-full min-h-[50vw] bg-[#e7e7e7] rounded-sm shadow-lg mx-auto"
                :key="video"
            ></iframe>
        </div>

        <div class="mx-2 pb-1">
            <input
                class="border-0 shadow appearance-none border rounded w-full p-1 leading-tight focus:outline-none focus:shadow-outline"
                type="text"
                placeholder="Enter YouTube Video URL..."
                v-model="videoSrc"
            />
        </div>
        <!-- class="w-full bg-[#e7e7e7] rounded-sm shadow-lg mx-auto" -->

        <div
            class="m-1 flex flex-col border rounded-md shadow-lg bg-[#ebebeb] min-h-[50vw]"
        >
            <div id="chat-messages" class="chat-messages"></div>
            <div class="flex-grow"></div>
            <div class="chat-input flex h-8 rounded-l-md">
                <input
                    id="question-input"
                    class="border-0 flex-grow h-8 rounded-bl-md text-sm px-1 py-0"
                    type="text"
                    placeholder="Type Your Question Here..."
                />
                <a
                    class="hover:cursor-pointer flex justify-center items-center h-8 py-auto ext-center p-1 text-xs bg-red-500 text-white rounded-r-md"
                    id="send-question"
                    >Send</a
                >
                <a
                    id="download-transcript"
                    class="flex justify-center items-center w-8 bg-white download-transcript"
                >
                    <img
                        src="/img/download.png"
                        alt="Download Transcript"
                        class="h-5"
                    />
                </a>
            </div>
        </div>
        <!-- <div class="twitter-logo-container">
            <div class="twitter-logo-container">
                <a
                    href="https://twitter.com/DreadMcLaren"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    <img
                        src="{{ url_for('static', filename='twitter.png') }}"
                        alt="Twitter Logo"
                    />
                </a>
            </div>
            <a
                href="https://www.buymeacoffee.com/dreadmclaren"
                target="_blank"
                class="buymeacoffee-logo-container"
            >
                <img
                    src="{{ url_for('static', filename='coffee.png') }}"
                    alt="Buy Me A Coffee"
                />
            </a>
        </div> -->
    </div>
</template>

<style></style>

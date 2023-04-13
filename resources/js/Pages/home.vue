<script setup>
import { Head, Link, usePage } from "@inertiajs/vue3";
import { ref, computed, onMounted, watch } from "vue";
import { debounce } from "lodash";

const videoSrc = ref("");
const current_user = ref(null);
const videoPlayer = ref(null);
const user = computed(() => usePage().props.user);
const hasPremium = computed(() => usePage().props.hasPremium);
const showInstructions = ref(false);
const debouncedInputTimer = ref(null);
const video = ref(null);
const loading = ref(false);
const chatMessages = ref(null);
const questionInput = ref("");
const refresher = ref(0);
const menuVisible = ref(false);

watch(
    videoSrc,
    debounce((newValue) => {
        // Handle onChange event here
        const videoUrl = newValue.trim();
        if (!videoUrl) {
            loading.value = false;
            return;
        }

        const videoId = extractVideoId(videoUrl);

        if (!videoId) {
            alert("Please enter a valid YouTube URL");
            loading.value = false;
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

        loading.value = false;
        video.value = embedUrl;
    }, 1500)
);

function extractVideoId(videoUrl) {
    const regex =
        /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/?)|youtu\.be\/)([\w-]{11})/;
    const match = videoUrl.match(regex);
    return match ? match[1] : null;
}

function askQuestion() {
    const question = questionInput.value.trim();
    if (!question) return;

    displayMessage("You: " + question, "user-message");
    questionInput.value = "";

    const aiMessageElement = displayMessage("AI: ", "ai-message", true);
    const loadingDots = aiMessageElement.querySelector(".loading-dots");
    loadingDots.style.display = "inline-block";
    axios
        .post("/ask", {
            video_url: videoSrc.value.trim(),
            question,
        })
        .then((data) => {
            const answer = data.data.answer;
            aiMessageElement.textContent = "AI: " + answer;
        })
        .catch((error) => {
            console.error("Error:", error);
            const answer = error.response.data.answer;
            aiMessageElement.textContent = "Error: " + answer;
            aiMessageElement.style.backgroundColor = "yellow";
        })
        .finally(() => {
            loadingDots.style.display = "none";
        });
}
onMounted(() => {
    google.accounts.id.initialize({
        client_id:
            "391724086841-egb5ffs77sss0gqnart3c45q3fkvshde.apps.googleusercontent.com",
        callback: handleCredentialResponse,
    });
    google.accounts.id.renderButton(
        document.getElementById("buttonDiv"),
        { theme: "outline", size: "large" } // customization attributes
    );
    google.accounts.id.prompt(); // also display the One Tap dialog
});
function downloadTranscript() {
    let transcript = "";
    chatMessages.value
        .querySelectorAll(".user-message, .ai-message")
        .forEach((messageElement) => {
            transcript += messageElement.textContent + "\n";
        });
    transcript += "\n" + "YouTube Video URL: " + videoSrc.value.trim();

    const currentDate = new Date();
    const formattedDate = currentDate.toISOString().slice(0, 10);

    const blob = new Blob([transcript], {
        type: "text/plain;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "TubeAsk_Transcript_" + formattedDate + ".txt";
    link.click();
    URL.revokeObjectURL(url);
}

function displayMessage(message, className, isAI = false) {
    const messageElement = document.createElement("div");
    messageElement.classList.add(className);
    messageElement.textContent = message;

    if (isAI) {
        const loadingDots = document.createElement("div");
        loadingDots.classList.add("loading-dots");
        loadingDots.innerHTML = "<span></span><span></span><span></span>";
        messageElement.appendChild(loadingDots);
    }

    chatMessages.value.appendChild(messageElement);
    chatMessages.value.scrollTop = chatMessages.scrollHeight;
    return messageElement;
}

setInterval(function () {
    refresher.value = refresher.value + 1;
}, 1000);
</script>

<template>
    <Head title="TubeAsk" />

    <div
        class="flex flex-col md:flex-row items-center justify-between px-4 py-3 bg-transparent"
    >
        <div>
            <a href="#" class="text-lg font-semibold text-white">TubeAsk</a>
        </div>
        <div class="relative inline-block text-left">
            <div>
                <button
                    type="button"
                    class="inline-flex justify-center w-full px-4 py-2 bg-transparent text-sm font-medium text-white focus:outline-none focus:ring-0 focus:ring-0 focus:ring-0"
                    id="menu-button"
                    aria-expanded="true"
                    aria-haspopup="true"
                    @click="menuVisible = !menuVisible"
                    @blur="
                        debounce(function () {
                            menuVisible = false;
                        }, 300)
                    "
                >
                    <span v-if="user" class="text-white">
                        {{ user.email }}
                    </span>
                    <div id="buttonDiv"></div>
                    <svg
                        class="-mr-1 ml-2 h-5 w-5"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                        aria-hidden="true"
                        v-if="user"
                    >
                        <path
                            fill-rule="evenodd"
                            d="M5.293 7.707a1 1 0 0 1 1.414 0L10 11.586l3.293-3.293a1 1 0 1 1 1.414 1.414l-4 4a1 1 0 0 1-1.414 0l-4-4a1 1 0 0 1 0-1.414z"
                            clip-rule="evenodd"
                        />
                    </svg>
                </button>
            </div>
            <div
                v-if="menuVisible && user"
                class="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5"
                role="menu"
                aria-orientation="vertical"
                aria-labelledby="menu-button"
                tabindex="-1"
            >
                <div class="py-1" role="none">
                    <a
                        href="#"
                        class="text-gray-700 block px-4 py-2 text-sm"
                        role="menuitem"
                        tabindex="-1"
                        id="menu-item-0"
                        >Link 1</a
                    >
                    <a
                        href="#"
                        class="text-gray-700 block px-4 py-2 text-sm"
                        role="menuitem"
                        tabindex="-1"
                        id="menu-item-1"
                        >Link 2</a
                    >
                    <a
                        class="text-gray-700 block px-4 py-2 text-sm"
                        role="menuitem"
                        tabindex="-1"
                        v-if="user"
                        href="/logout"
                        >Logout</a
                    >
                </div>
            </div>
        </div>

        <!-- <nav class="hidden md:mt-0 mt-4 md:flex flex-col md:flex-row">
            <a href="/logout">Logout</a>
            <div @click="showInstructions = true">Instructions</div>
            <div>
                <a v-if="!user" class="w-full h-full" href="/login">
                    Login with Google
                </a>
                <a v-if="user" class="w-full h-full" href="javascript:;">
                    {{ user.email }}
                </a>
            </div>
            <div v-if="user">
                <a v-if="!hasPremium" class="logout" href="/upgrade">
                    Upgrade</a
                >
                <a v-if="hasPremium" href="/edit-subscription">
                    Edit Subscription
                </a>
            </div>
        </nav> -->
    </div>
    <div
        v-if="showInstructions"
        class="fixed top-0 left-0 w-full h-full flex items-center justify-center"
    >
        <div
            class="bg-[#ffe0e1] p-8 justify-center flex flex-col rounded-lg shadow-lg border border-3 border-black"
        >
            <h2 class="text-lg font-bold mb-4 text-center">Instructions</h2>
            <div class="instructions-modal-content mb-8">
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
            <button
                class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                @click="showInstructions = false"
            >
                Close
            </button>
        </div>
    </div>

    <div
        class="max-w-[600px] bg-[#ffe0d1] p-2 rounded-md my-auto mx-auto"
        style="
            box-shadow: 0 12px 16px rgba(0, 0, 0, 0.24),
                0 10px 14px rgba(0, 0, 0, 0.24);
        "
    >
        <h2 class="subtitle text-center">Summarize YouTube Videos Using AI</h2>
        <h2 class="text-center"><small v-if="loading">Loading Video</small></h2>

        <div class="p-2 rounded-lg">
            <iframe
                ref="videoPlayer"
                id="video-player"
                :src="video"
                frameborder="0"
                allowfullscreen
                class="w-full min-h-[300px] bg-[#e7e7e7] rounded-sm shadow-lg mx-auto"
                :key="video"
            ></iframe>
        </div>

        <div class="mx-2">
            <input
                class="border-0 shadow appearance-none border rounded w-full p-1 leading-tight focus:outline-none focus:shadow-outline"
                type="text"
                placeholder="Enter YouTube Video URL..."
                v-model="videoSrc"
                @input="loading = true"
            />
        </div>
        <div class="mx-2">
            <div
                class="m-3 flex flex-col border w-full min-h-[300px] bg-[#e7e7e7] rounded-sm shadow-lg mx-auto"
            >
                <div ref="chatMessages" class="p-2 chat-messages"></div>
                <div class="flex-grow">
                    <span class="loading-dots"> </span>
                </div>
                <div class="chat-input flex h-8 rounded-l-md">
                    <input
                        id="question-input"
                        class="border-0 flex-grow h-8 rounded-bl-md text-sm px-1 py-0"
                        type="text"
                        v-model="questionInput"
                        @keydown.enter="askQuestion()"
                        placeholder="Type Your Question Here..."
                    />
                    <a
                        class="hover:cursor-pointer flex justify-center items-center h-8 py-auto ext-center p-1 text-xs bg-red-500 text-white rounded-r-md"
                        id="send-question"
                        @click="askQuestion()"
                        >Send</a
                    >
                    <a
                        id="download-transcript"
                        class="flex justify-center items-center w-8 bg-white download-transcript"
                        @click="downloadTranscript()"
                    >
                        <img
                            src="/img/download.png"
                            alt="Download Transcript"
                            class="h-5 cursor-pointer"
                        />
                    </a>
                </div>
            </div>
        </div>
        <div class="fixed bottom-3 flex left-3">
            <a
                href="https://twitter.com/DreadMcLaren"
                target="_blank"
                rel="noopener noreferrer"
                class="mr-3"
            >
                <img src="/img/twitter.png" class="h-6" alt="Twitter Logo" />
            </a>
            <a
                href="https://www.buymeacoffee.com/dreadmclaren"
                target="_blank"
                class="buymeacoffee-logo-container"
            >
                <img
                    class="h-6"
                    src="/img/bmc-button.png"
                    alt="Buy Me A Coffee"
                />
            </a>
        </div>
    </div>
</template>

<style>
.loading-dots {
    display: none;
    width: 1.5rem;
    height: 1.5rem;
    position: relative;
    margin-left: 0.1rem;
    vertical-align: middle;
}

.loading-dots span {
    position: absolute;
    width: 0.5rem;
    height: 0.5rem;
    background-color: #333;
    border-radius: 50%;
    animation: loading-dots 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
    top: 0.5rem;
    left: 0;
    animation-delay: -0.4s;
}

.loading-dots span:nth-child(2) {
    top: 0.5rem;
    left: 0.7rem;
    animation-delay: -0.2s;
}

.loading-dots span:nth-child(3) {
    top: 0.5rem;
    left: 1.3rem;
    animation-delay: 0;
}

.user-message:hover,
.ai-message:hover {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12), 0 2px 2px rgba(0, 0, 0, 0.24);
}

#question-input::placeholder {
    color: #999;
    font-style: italic;
}

.chat-messages::-webkit-scrollbar {
    width: 8px;
}

.chat-messages::-webkit-scrollbar-thumb {
    background-color: #ccc;
    border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-track {
    background-color: #f0f0f0;
    border-radius: 4px;
}

.ai-message {
    display: flex;
    align-items: center;
}

.chat-messages {
    display: flex;
    flex-direction: column;
    height: calc(80vh - 500px);
    overflow-y: auto;
    padding: 0.5rem;
    white-space: pre-wrap;
    border-bottom: 1px solid #ccc;
    box-shadow: inset 0 -1px 1px rgba(0, 0, 0, 0.08);
}

.user-message,
.ai-message {
    display: flex;
    align-items: center;
    padding: 0.5rem;
    margin-bottom: 1rem;
    border-radius: 10px;
    max-width: 80%;
    line-height: 1.5;
    font-size: 16px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08), 0 1px 1px rgba(0, 0, 0, 0.16);
}

.user-message {
    background-color: #ff0000;
    color: #ffffff;
    margin-left: 0.5rem;
    font-weight: 500;
    align-self: flex-start;
}

.ai-message {
    background-color: #ffffff;
    color: #333333;
    margin-right: 0.5rem;
    font-weight: 500;
    align-self: flex-end;
}
/*  */

.chat-messages {
    display: flex;
    flex-direction: column;
    height: 300px;
    overflow-y: auto;
    padding: 0.5rem;
    white-space: pre-wrap;
    border-bottom: 1px solid #ccc;
    box-shadow: inset 0 -1px 1px rgba(0, 0, 0, 0.08);
}

.user-message,
.ai-message {
    display: flex;
    align-items: center;
    padding: 0.5rem;
    margin-bottom: 1rem;
    border-radius: 10px;
    max-width: 80%;
    line-height: 1.5;
    font-size: 16px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08), 0 1px 1px rgba(0, 0, 0, 0.16);
}

.user-message {
    background-color: #ff0000;
    color: #ffffff;
    margin-left: 0.5rem;
    font-weight: 500;
    align-self: flex-start;
}

.ai-message {
    background-color: #ffffff;
    color: #333333;
    margin-right: 0.5rem;
    font-weight: 500;
    align-self: flex-end;
}
@keyframes loading-dots {
    0%,
    80%,
    100% {
        transform: scaleY(0.4);
    }
    40% {
        transform: scaleY(1);
    }
}
</style>

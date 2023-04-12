<script setup>
import { Head, Link, usePage, router } from "@inertiajs/vue3";
import { ref, computed } from "vue";
import axios from "axios";

const successful = ref(false);
const user = computed(() => usePage().props.user);

async function checkUpgrade() {
    if (successful.value) {
        return;
    }
    setTimeout(async function () {
        try {
            const res = await axios.post("/has-subscribed", {});
            successful.value = true;
            router.visit("/");
        } catch (e) {
            console.log(e);
            checkUpgrade();
        }
    }, 500);
}
checkUpgrade();
</script>

<template>
    <Head title="TubeAsk" />
    <div class="flex justify-between">
        <div>
            <!-- <div
                id="instructions-button"
                class="rounded-md cursor-pointer text-bold m-2 py-1 px-2 hover:bg-[#f4f4f4] bg-[#ffe0d1] text-[#ff581a] shadow-md"
            >
                Instructions
            </div> -->
        </div>
        <div>
            <!-- <div v-if="current_user?.is_authenticated">
                <p class="user-info">Hello, {{ current_user.name }}!</p>
                <a
                    class="rounded-xl cursor-pointer text-bold m-2 py-1 px-2 hover:bg-[#f4f4f4] bg-[#ffe0d1] text-[#ff581a] shadow-md"
                    href="/logout"
                    >Logout</a
                >
            </div>
            <div
                class="rounded-md cursor-pointer text-bold mx-2 mt-2 p-1 hover:bg-[#f4f4f4] bg-[#ffe0d1] text-[#ff581a] shadow-md"
            >
                <a v-if="!user" class="w-full h-full" href="/login">
                    Login with Google
                </a>
                <a v-if="user" class="w-full h-full" href="javascript:;">
                    {{ user.email }}
                </a>
            </div>
            <div class="text-white text-center" v-if="user">
                <a class="logout" href="/upgrade"> Upgrade </a> |
                <a class="logout" href="/logout"> Logout </a>
            </div> -->
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
        class="max-w-[600px] bg-[#ffe0d1] p-2 rounded-md my-auto mx-auto mt-5"
        style="
            box-shadow: 0 12px 16px rgba(0, 0, 0, 0.24),
                0 10px 14px rgba(0, 0, 0, 0.24);
        "
    >
        <h1 class="text-2xl text-center">TubeAsk</h1>
        <h2 class="subtitle text-center">Verifying your payment.</h2>

        <div class="p-2 rounded-lg"></div>

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

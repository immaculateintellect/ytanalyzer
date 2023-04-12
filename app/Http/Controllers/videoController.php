<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class videoController extends Controller
{
    //
    function extract_video_id($video_url) {
        $patterns = array(
            '/(?:https?:\/\/)?(?:www\.|m\.)?(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([\w-]{11})/',
            '/(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/shorts\/)([\w-]{11})(?:\?.*)?/'
        );

        foreach ($patterns as $pattern) {
            preg_match($pattern, $video_url, $matches);
            if (!empty($matches)) {
                return $matches[1];
            }
        }

        return null;
    }
}

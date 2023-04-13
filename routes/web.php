<?php

use App\Http\Controllers\ProfileController;
use Illuminate\Foundation\Application;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Process;
use Inertia\Inertia;
use App\Models\User;
use Illuminate\Http\Request;
use OpenAI\Laravel\Facades\OpenAI;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/



Route::get('/login/google/authorized', function (Request $request) {
    try {
        $user = Socialite::driver('google')->user();
    } catch (\Exception $e) {
        return redirect('/');
    }
    // check if they're an existing user
    $existingUser = User::where('email', $user->email)->first();

    if($existingUser){
        // log them in
        auth()->login($existingUser, true);
    } else {
        // create a new user
        $newUser                  = new User;
        $newUser->name            = $user->name;
        $newUser->email           = $user->email;
        $newUser->password           = bcrypt(Str::random(20));
        $newUser->save();
        auth()->login($newUser, true);
    }

    return redirect()->to('/');

});
Route::post('/stripe/webhooks', '\Laravel\Cashier\Http\Controllers\WebhookController@handleWebhook');

Route::get('/upgrade', function (Request $request) {
  Auth::user()->createOrGetStripeCustomer();

  return Auth::user()->newSubscription('default', env('PRICE_ID'))->checkout([
        'success_url' => route('checkout-success').'?session_id={CHECKOUT_SESSION_ID}',
        'cancel_url' => route('checkout-cancel'),
    ]);
});

Route::get('/success',function(Request $req){
    return Inertia::render('verifyPayment');
})->name('checkout-success');

Route::post('/has-subscribed', function (Request $req){
  if(Auth::user()->subscribed('default')){
    return response('',200);
  }else{
    return response('',500);
  }
});

Route::get('/failed',function(){return redirect('/');})->name('checkout-cancel');

Route::get('/', function () {
    $user = Auth::user();
    $hasPremium = false;

    if($user){
        $hasPremium = Auth::user()->subscribed('default');
    }
    return Inertia::render('home', [
        'user'=>$user,
        'hasPremium'=>$hasPremium
    ]);
})->name('home');

Route::get('/login', function () {
    return Socialite::driver('google')->redirect();
});

Route::post('/ask', function (Request $request) {
    try {

    $yourApiKey = env('OPENAI_API_KEY');
    $client = OpenAI::client($yourApiKey);

    $video_url = $request->video_url;
    $question = $request->question;
    
    Log::info("Received video_url: $video_url");
      if (!$video_url) {
        throw new \Exception('Add a video URL');
      }

      if (!$question) {
        throw new \Exception('Missing question');
      }
   
    
    if(!$video_id = app(\App\Http\Controllers\videoController::class)->extract_video_id($video_url)){
        throw new \Exception('Invalid video URL format');
    }
    $video_info_url = "https://www.googleapis.com/youtube/v3/videos?id=$video_id&part=snippet,statistics,contentDetails&key=".env('YOUTUBE_API_KEY');
    $response = Http::get($video_info_url);

    $video_info = $response->json();

    $title = $video_info['items'][0]['snippet']['title'];
    $description = $video_info['items'][0]['snippet']['description'];
    $channel_title = $video_info['items'][0]['snippet']['channelTitle'];
    $published_at = $video_info['items'][0]['snippet']['publishedAt'];

    $statistics = $video_info['items'][0]['statistics'];
    $view_count = isset($statistics['viewCount']) ? $statistics['viewCount'] : 'N/A';
    $like_count = isset($statistics['likeCount']) ? $statistics['likeCount'] : 'N/A';
    $dislike_count = isset($statistics['dislikeCount']) ? $statistics['dislikeCount'] : 'N/A';
    $comment_count = isset($statistics['commentCount']) ? $statistics['commentCount'] : 'N/A';

    $content_details = $video_info['items'][0]['contentDetails'];
    $duration = isset($content_details['duration']) ? $content_details['duration'] : 'N/A';

    if($duration){
        $timeInterval      = new DateInterval($duration);
        $intervalInSeconds = (new DateTime())->setTimeStamp(0)->add($timeInterval)->getTimeStamp();
        $intervalInMinutes = $intervalInSeconds/60;
        if($intervalInMinutes>10 && (!Auth::user() || !Auth::user()->subscribed('default'))){
            throw new \Exception("You must be a premium member to ask about videos longer than 10 minutes.");
        }
        
    }

    $channel_id = $video_info['items'][0]['snippet']['channelId'];
    $channel_info_url = "https://www.googleapis.com/youtube/v3/channels?id={$channel_id}&part=statistics&key=".env('YOUTUBE_API_KEY');

    $response = Http::get($channel_info_url);
    $channel_info = $response->json();

    $subscriber_count = isset($channel_info['items'][0]['statistics']) ? $channel_info['items'][0]['statistics']['subscriberCount'] : 'N/A';
    $script = base_path()."/getTranscriptById.py";
    $command  = "python3 $script $video_id";

    $result = Process::run($command);
    $transcript=$result->output();
    $system_message = "This is a video titled '".
    truncate($title, 25).
    "' by '"."$channel_title' with the description: '".
    truncate($description, 160)."'. The video was published on 
    $published_at and has $view_count views, 
    $like_count likes, $dislike_count dislikes, and $comment_count comments. The video duration is 
    $duration and the channel has $subscriber_count subscribers.";

    if($transcript!==""){
        $system_message = $system_message." The video has the following transcript: '".truncate($transcript, 16030)."'";
    }
    Log::info('system message: '.$system_message);
    Log::info("Question: ".$question);

    $response = $client->chat()->create([
        'model' => 'gpt-3.5-turbo',
        'messages' => [
            ['role' => 'system', 'content' => $system_message],
            ['role' => 'user', 'content' => $question],
        ],
    ]);

    $answer = $response['choices'][0]['message']['content'];


     } catch (\Exception $error) {
      return response()->json([
        'answer' => $error->getMessage(),
        'error' => $error,
      ],500);
    }

    return response()->json([ "answer"=> $answer]);

});

Route::get('/edit-subscription', function () {
    return Auth::user()->redirectToBillingPortal();
});



Route::get('/logout', function () {
    Auth::logout();
    return redirect()->to('/');
});


function truncate($string, $length) {
    if (strlen($string) > $length) {
        $string = substr($string, 0, $length - 3) . '...';
    }
    return $string;
}
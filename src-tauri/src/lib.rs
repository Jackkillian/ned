use chlorine::{scan_dir, Song};
use std::path::Path;
use std::sync::Mutex;
use tauri::{AppHandle, Emitter, Manager};
use tauri::{TitleBarStyle, WebviewUrl, WebviewWindowBuilder};

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
async fn scan(path: String) -> Result<Vec<Song>, String> {
    let target_path = Path::new(&path);

    if !target_path.exists() {
        return Err("Directory does not exist".to_string());
    }

    tokio::task::spawn_blocking(move || scan_dir(&path).map_err(|e| e.to_string()))
        .await
        .map_err(|e| e.to_string())?
}

fn setup_window(app: &AppHandle, url: WebviewUrl, title: &str) {
    let win_builder = WebviewWindowBuilder::new(app, "main", url)
        .title(title)
        // .transparent(true)
        .decorations(false)
        .inner_size(800.0, 600.0);

    // set transparent title bar only when building for macOS
    #[cfg(target_os = "macos")]
    let win_builder = win_builder.title_bar_style(TitleBarStyle::Transparent);

    let _window = win_builder.build().unwrap();

    // set background color only when building for macOS
    // #[cfg(target_os = "macos")]
    // {
    //     use objc2_app_kit::{NSColor, NSWindow};
    //
    //     let ns_window_ptr = window.ns_window().unwrap() as *mut NSWindow;
    //     let ns_window = unsafe { &*ns_window_ptr };
    //     let bg_color = NSColor::colorWithRed_green_blue_alpha(
    //         220.0 / 255.0,
    //         220.0 / 255.0,
    //         220.0 / 255.0,
    //         0.97,
    //     );
    //     ns_window.setBackgroundColor(Some(&bg_color));
    // }
}

fn player_start_song(app: &AppHandle, url: &str) {
    let window = match app.get_webview_window("player") {
        Some(window) => window,
        None => {
            // create a new window
            let builder =
                WebviewWindowBuilder::new(app, "player", WebviewUrl::App("/player".into()))
                    .title("Player")
                    .always_on_top(true)
                    .transparent(true)
                    .decorations(false)
                    .inner_size(440.0, 112.0);
            builder.build().expect("Could not create player window")
        }
    };
    app.emit_to("player-start", "player", url).unwrap();
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        // .manage(Mutex::new(SetupState {
        //     frontend_task: false,
        //     backend_task: false,
        // }))
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet, scan])
        .setup(|app| {
            // setup_window(app.handle(), WebviewUrl::default(), "Ned");
            let builder = WebviewWindowBuilder::new(
                app.handle(),
                "player",
                WebviewUrl::App("/player".into()),
            )
            .title("Player")
            .always_on_top(true)
            .transparent(true)
            .decorations(false)
            .accept_first_mouse(true)
            .inner_size(440.0, 112.0);
            builder.build().expect("Could not create player window");
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

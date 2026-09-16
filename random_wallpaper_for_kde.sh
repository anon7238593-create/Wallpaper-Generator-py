BASE_URL="https://anon7238593-create.github.io/Wallpaper-Generator-py"

COUNT=$(curl -sSL "${BASE_URL}/count.txt")
COUNT=$(echo "$COUNT" | tr -dc '0-9')
if ! [[ "$COUNT" =~ ^[0-9]+$ ]] || [ "$COUNT" -lt 1 ]; then
    echo "Bad COUNT: '$COUNT'" >&2
    exit 1
fi
echo "Count = $COUNT"

random_num=$(shuf -i 1-"$COUNT" -n 1)
echo "Downloading wallpaper #$random_num..."

WALLPAPER_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/wallpapers"
mkdir -p "$WALLPAPER_DIR"
TARGET_FILE="${WALLPAPER_DIR}/wallpaper-${random_num}_$(date +%s).png"

if ! curl -sS -f -o "$TARGET_FILE" "${BASE_URL}/wallpapers/wallpaper-${random_num}.png"; then
    echo "Download failed" >&2
    exit 1
fi

# Remove previous wallpapers to save disk space
find "$WALLPAPER_DIR" -type f -name "wallpaper-*.png" ! -name "$(basename "$TARGET_FILE")" -delete

# Apply to desktop
plasma-apply-wallpaperimage "$TARGET_FILE"

# Apply to lock screen (KDE Plasma 6)
kwriteconfig6 --file kscreenlockerrc --group Greeter --key WallpaperPlugin "org.kde.image"
kwriteconfig6 --file kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image --group General --key Image "file://${TARGET_FILE}"
echo "Wallpaper set for desktop and lock screen: $TARGET_FILE"

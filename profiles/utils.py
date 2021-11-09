def game_alias(profile_instance):
    try:
        # The currently supported formats are png, jpg, jpeg, bmp, gif, webp, psd (iOS only) - RN Image Component
        return {
            "alias": profile_instance.lol_profile.name,
            "logo": "https://ubuntuhandbook.org/wp-content/uploads/2018/09/lol-icon.png",
        }
    except Exception:
        return {"alias": "", "logo": ""}

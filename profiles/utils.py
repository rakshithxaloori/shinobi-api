lol_logo = "https://www.shinobi.cc/league_of_legends-256x256.png"


def game_alias(profile_instance):
    try:
        # The currently supported formats are png, jpg, jpeg, bmp, gif, webp, psd (iOS only) - RN Image Component
        return {
            "alias": profile_instance.lol_profile.name,
            "logo": lol_logo,
        }
    except Exception:
        return {"alias": "", "logo": ""}

from get_iplayer_downloader import get_iplayer

def list_categories():
    #NOTE end="" suppresses newline: print("...", end="")

    # Avoid refresh messages in the print statements below
    get_iplayer.refresh()
    print()

    categories = get_iplayer.categories("", get_iplayer.Preset.RADIO, get_iplayer.ProgType.PODCAST)
    print("[radio]")
    print("categories-podcast =", categories)
    
    categories = get_iplayer.categories("", get_iplayer.Preset.RADIO, get_iplayer.ProgType.RADIO)
    print("categories-radio =", categories)
    print()

    categories = get_iplayer.categories("", get_iplayer.Preset.TV, get_iplayer.ProgType.TV)
    print("[tv]")
    print("categories =", categories)

def list_channels(compact=True):
    # Avoid refresh messages in the print statements below
    get_iplayer.refresh()
    print()

    channels = get_iplayer.channels("", get_iplayer.Preset.RADIO, get_iplayer.ProgType.RADIO + "," + get_iplayer.ProgType.PODCAST, compact=compact)
    print("[radio]")
    print("channels =", channels)
    print()

    channels = get_iplayer.channels("", get_iplayer.Preset.TV, get_iplayer.ProgType.TV, compact=compact)
    print("[tv]")
    print("channels =", channels)

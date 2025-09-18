import pytest

@pytest.fixture(autouse=True)
def _inmemory_channels(settings):
    # Use in-memory channel layer for every test (no Redis needed)
    settings.CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
    }

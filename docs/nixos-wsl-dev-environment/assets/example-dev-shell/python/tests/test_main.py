from main import greeting


def test_greeting() -> None:
    assert greeting("Nix") == "Hello, Nix!"

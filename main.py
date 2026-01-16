from library_core import CLI

def main():
    """Entrypoint for app."""
    try:
        app = CLI()
        app.run()
    except KeyboardInterrupt:
        print("\nCancelled by user. Shutting down...")
    except Exception as e:
        print(f"\nAn unexpected error: {e}")

if __name__ == "__main__":
    main()
from src.app import App, Config


def main():
    config = Config()
    app = App(config)
    app.run()


if __name__ == "__main__":
    main()

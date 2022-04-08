from lib.tcp import TCP

ROUTER_IP = "0.0.0.0"
ROUTER_PORT = 3000


def main():
    t = TCP(ROUTER_IP, ROUTER_PORT)
    t.connect(3001, 3002)


if __name__ == "__main__":
    main()

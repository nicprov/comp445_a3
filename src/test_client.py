from lib.tcp import TCP

ROUTER_IP = "0.0.0.0"
ROUTER_PORT = 3000


def main():
    t = TCP(ROUTER_IP, ROUTER_PORT)
    t.connect(3001, 3002)

    t.send("""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Tempus urna et pharetra pharetra massa massa ultricies. Vitae congue eu consequat ac felis donec et. Suscipit tellus mauris a diam maecenas sed enim ut. Eget nullam non nisi est sit amet. Euismod nisi porta lorem mollis aliquam ut porttitor leo. Quis hendrerit dolor magna eget est lorem. Faucibus interdum posuere lorem ipsum dolor sit. Et ultrices neque ornare aenean euismod elementum. Quam lacus suspendisse faucibus interdum. Amet volutpat consequat mauris nunc. Egestas integer eget aliquet nibh praesent tristique magna. Ridiculus mus mauris vitae ultricies leo integer malesuada nunc. Eget egestas purus viverra accumsan in. Faucibus nisl tincidunt eget nullam non nisi est sit amet. Habitant morbi tristique senectus et netus. Sed egestas egestas fringilla phasellus faucibus scelerisque eleifend donec. Eros donec ac odio tempor.""")

if __name__ == "__main__":
    main()

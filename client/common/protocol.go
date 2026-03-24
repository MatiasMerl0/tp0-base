package common

import (
	"encoding/binary"
	"fmt"
	"io"
	"net"
)

func SendMessage(conn net.Conn, msg string) error {
	data := []byte(msg)
	length := uint32(len(data))

	if err := binary.Write(conn, binary.BigEndian, length); err != nil {
		return fmt.Errorf("failed to send message header: %w", err)
	}

	totalSent := 0
	for totalSent < len(data) {
		n, err := conn.Write(data[totalSent:])
		if err != nil {
			return fmt.Errorf("failed to send message body: %w", err)
		}
		totalSent += n
	}

	return nil
}

func ReceiveMessage(conn net.Conn) (string, error) {
	var length uint32
	if err := binary.Read(conn, binary.BigEndian, &length); err != nil {
		return "", fmt.Errorf("failed to read message header: %w", err)
	}

	buf := make([]byte, length)
	if _, err := io.ReadFull(conn, buf); err != nil {
		return "", fmt.Errorf("failed to read message body: %w", err)
	}

	return string(buf), nil
}

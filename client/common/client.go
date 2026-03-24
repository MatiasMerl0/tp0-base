package common

import (
	"context"
	"fmt"
	"net"
	"os"
	"os/signal"
	"syscall"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	Name          string
	Surname       string
	Document      string
	Birthdate     string
	Number        string
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	ctx    context.Context
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	ctx, cancel := context.WithCancel(context.Background())
	client := &Client{
		config: config,
		ctx:    ctx,
	}

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGTERM)
	go func() {
		<-sigChan
		log.Infof("action: sigterm_received | result: success | client_id: %v", config.ID)
		cancel()
	}()

	return client
}

func (c *Client) createClientSocket() error {
	dialer := net.Dialer{}
	conn, err := dialer.DialContext(c.ctx, "tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	c.conn = conn
	return nil
}

func (c *Client) StartClientLoop() {
	if err := c.createClientSocket(); err != nil {
		return
	}

	bet := fmt.Sprintf("BET\n%s\n%s\n%s\n%s\n%s\n%s",
		c.config.ID,
		c.config.Name,
		c.config.Surname,
		c.config.Document,
		c.config.Birthdate,
		c.config.Number,
	)

	if err := SendMessage(c.conn, bet); err != nil {
		log.Errorf("action: apuesta_enviada | result: fail | client_id: %v | error: %v", c.config.ID, err)
		c.conn.Close()
		return
	}

	response, err := ReceiveMessage(c.conn)
	c.conn.Close()

	if err != nil {
		log.Errorf("action: apuesta_enviada | result: fail | client_id: %v | error: %v", c.config.ID, err)
		return
	}

	if response == "OK" {
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
			c.config.Document, c.config.Number)
	} else {
		log.Errorf("action: apuesta_enviada | result: fail | client_id: %v | response: %v", c.config.ID, response)
	}
}

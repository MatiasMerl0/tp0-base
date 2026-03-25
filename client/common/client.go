package common

import (
	"context"
	"net"
	"os"
	"os/signal"
	"syscall"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type ClientConfig struct {
	ID            string
	ServerAddress string
	MaxAmount     int
}

type Client struct {
	config ClientConfig
	conn   net.Conn
	ctx    context.Context
}

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
	bets, err := ReadBets("/data/agency.csv") // mounted in container volume
	if err != nil {
		log.Errorf("action: read_bets | result: fail | client_id: %v | error: %v", c.config.ID, err)
		return
	}

	if err := c.createClientSocket(); err != nil {
		return
	}
	defer c.conn.Close()

	for i := 0; i < len(bets); i += c.config.MaxAmount {
		select {
		case <-c.ctx.Done(): // Graceful shutdown between batches
			log.Infof("action: shutdown | result: success | client_id: %v", c.config.ID)
			return
		default:
		}

		end := i + c.config.MaxAmount
		if end > len(bets) { // If its last batch
			end = len(bets)
		}
		batch := bets[i:end]

		msg := SerializeBatch(c.config.ID, batch)
		if len(msg) > MaxBatchBytes {
			log.Errorf("action: apuesta_enviada | result: fail | client_id: %v | error: batch exceeds 8kB limit", c.config.ID)
			return
		}

		if err := SendMessage(c.conn, msg); err != nil {
			log.Errorf("action: apuesta_enviada | result: fail | client_id: %v | error: %v", c.config.ID, err)
			return
		}

		response, err := ReceiveMessage(c.conn)
		if err != nil {
			log.Errorf("action: apuesta_enviada | result: fail | client_id: %v | error: %v", c.config.ID, err)
			return
		}

		if response != "OK" {
			log.Errorf("action: apuesta_enviada | result: fail | client_id: %v | response: %v", c.config.ID, response)
			return
		}
	}

	log.Infof("action: apuesta_enviada | result: success | client_id: %v | bets_sent: %v", c.config.ID, len(bets))
}

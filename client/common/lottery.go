package common

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

const MaxBatchBytes = 8 * 1024 // 8kiB

type Bet struct {
	Name      string
	Surname   string
	Document  string
	Birthdate string
	Number    string
}

// ReadBets reads all bets from a CSV file with format: name,surname,document,birthdate,number
func ReadBets(filePath string) ([]Bet, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to open bets file: %w", err)
	}
	defer file.Close() // closes the file at the end of the function no matter the result.

	var bets []Bet
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		fields := strings.Split(scanner.Text(), ",")
		if len(fields) != 5 {
			return nil, fmt.Errorf("invalid bet line: %s", scanner.Text())
		}
		bets = append(bets, Bet{
			Name:      fields[0],
			Surname:   fields[1],
			Document:  fields[2],
			Birthdate: fields[3],
			Number:    fields[4],
		})
	}

	if err := scanner.Err(); err != nil {
		return nil, fmt.Errorf("failed to read bets file: %w", err)
	}

	return bets, nil
}

// SerializeBatch builds the protocol message for a batch of bets.
// Format: BATCH\n{agency}\n{count}\n{name},{surname},{doc},{birth},{num}\n...
func SerializeBatch(agency string, bets []Bet) string {
	lines := []string{"BATCH", agency, fmt.Sprintf("%d", len(bets))}
	for _, b := range bets {
		lines = append(lines, fmt.Sprintf("%s,%s,%s,%s,%s", b.Name, b.Surname, b.Document, b.Birthdate, b.Number))
	}
	return strings.Join(lines, "\n")
}

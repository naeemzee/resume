CREATE TABLE IF NOT EXISTS `cards` (
`card_id`         int(11) NOT NULL                        COMMENT 'the id of the card',
`board_id`        int(11) NOT NULL                        COMMENT 'the id of the board that this card is part of',
`list_id`         varchar(100) NOT NULL                   COMMENT 'the id of the list the card belongs to', 
`text`            varchar(100)                            COMMENT 'the text of the card',
PRIMARY KEY (`card_id`),
FOREIGN KEY (board_id) REFERENCES boards(board_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains cards asscociated with boards";
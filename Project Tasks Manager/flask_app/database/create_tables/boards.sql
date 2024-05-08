CREATE TABLE IF NOT EXISTS `boards` (
`board_id`         int(11) NOT NULL auto_increment         COMMENT 'the id of the board',
`user_id`          int(11) NOT NULL                        COMMENT 'the id of the user who owns this board',
`board_name`       varchar(100) NOT NULL                   COMMENT 'the name of the board',
`member_emails`    varchar(100)                            COMMENT 'the emails of the associated members for this board',
PRIMARY KEY (`board_id`),
FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Contains boards associated with users";

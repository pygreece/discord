NEW_MEMBER_MESSAGE = (
    "Γειά σου {name}, καλωσόρισες στο {guild}! 😊\n\n"
    "Οταν βρεις λίγο χρόνο, σε παρακαλώ διάβασε τον [Κώδικα Δεοντολογίας μας]({link}) "
    "και αντίδρασε με thumbs-up (👍) στο μήνυμα. Μόλις το κάνεις, "
    "θα σου δώσω τον απαραίτητο ρόλο ώστε να δεις όλα τα υπόλοιπα κανάλια και να "
    "συμμετέχεις στη συζήτηση!\n\n"
    "---\n\n"
    "Hey {name}, thanks for joining {guild}! 😊\n\n"
    "Whenever you find some time, please go through [our Code of Conduct]({link}) "
    "and react with a thumbs-up (👍) on the message. As soon as you do, I'll give you "
    "permissions to see all the other channels and join in on the fun! "
)

ALREADY_EXISTS_MESSAGE = (
    "Γειά σου {name}, καλωσόρισες ξανά στο {guild}! Χαίρομαι που είσαι πάλι μαζί μας! 😊\n\n"
    "Μπορείς να αντιδράσεις με thumbs-up (👍) στον [Κώδικα Δεοντολογίας μας]({link}) "
    "για να σου δώσω τον απαραίτητο ρόλο ώστε να δεις όλα τα υπόλοιπα κανάλια και να "
    "συμμετέχεις στη συζήτηση!\n\n"
    "---\n\n"
    "Hey {name}, we see that you re-joined {guild}! It's great to have you back! 😊\n\n"
    "You can react with a thumbs-up (👍) to [our Code of Conduct]({link}). "
    "As soon as you do, I'll give you permissions to see all the other channels "
    "and join in on the fun! "
)

### Ticket messages
NEW_MEMBER_TICKET_MESSAGE = (
    "Είσαι επίσημα μέλος {name}! Μήπως έχεις και εισιτήριο για το pycon Greece 2025; Στείλε στο τσατ !ticket "
    "κενό και τον αριθμό του εισιτήριου σου για να αποκτήσεις πρόσβαση στα κανάλια της "
    "εκδήλωσης! 😊\n\n"
    "---\n\n"
    "You are officialy a member {name}! Do you also happen to have a ticket for pycon Greece 2025? Reply with !ticket space "
    "and your ticket number in this chat to get access to the channels of the event! 😊 "
)

ASK_FOR_TICKET_MESSAGE = (
    "Γειά σου {name}, έχεις εισιτήριο για το pycon Greece 2025; Στείλε στο τσατ !ticket "
    "κενό και τον αριθμό του εισιτήριου σου για να αποκτήσεις πρόσβαση στα κανάλια της "
    "εκδήλωσης! 😊\n\n"
    "---\n\n"
    "Hey {name}, do you happen to have a ticket for pycon Greece 2025? Send !ticket space "
    "and your ticket number to get access to the channels of the event! 😊 "
)

### Ticket Errors
TICKET_INVALID_THREAD_MESSAGE = (
    "Αυτή η εντολή μπορεί να χρησιμοποιηθεί μόνο στο προσωπικό σου νήμα στο κανάλι για τα εισιτήρια. "
    "Αν δεν υπάρχει νήμα τότε αντίδρασε με ένα thumbs-up (👍) στο [μήνυμα για τα εισιτήρια]({link}).\n\n"
    "---\n\n"
    "This command can only be used in the user's thread in the ticket channel. "
    "Please react to the [ticket message]({link}) with a thumbs-up (👍) if the thread is missing. "
)

TICKET_ID_MISSING_MESSAGE = (
    "Παρακαλώ συμπερίλαβε τον αριθμό του εισιτηρίου μετά το !ticket.\n\n"
    "---\n\n"
    "Please provide a ticket ID after !ticket. "
)

TICKET_INVALID_ID_MESSAGE = (
    "Λάθος αριθμός εισιτηρίου, παρακαλώ ξαναπροσπάθησε.\n\n"
    "---\n\n"
    "Invalid ticket ID, please try again. "
)

TICKET_MEMBER_ALREADY_CLAIMED_MESSAGE = (
    "Έχεις ήδη επικυρώσει ένα εισιτήριο! 😊\n\n---\n\nYou have already claimed a ticket! 😊\n\n"
)

COC_NOT_ACCEPTED_MESSAGE = (
    "Δεν έχεις δεχτεί τον [Κώδικα Δεοντολογίας]({link}), "
    "παρακαλώ αντίδρασε με ένα thumbs-up (👍) στο [μήνυμα]({link}).\n\n"
    "---\n\n"
    "You have not accepted the [Code of Conduct]({link}), "
    "please react with a thumbs-up (👍) on the [message]({link}). "
)

TICKET_MEMBER_ALREADY_CLAIMED_WITH_NO_ROLE_MESSAGE = (
    "Έχεις ήδη επικυρώσει ένα εισιτήριο! Παρ' όλ' αυτά, κάτι περίεργο συνέβη "
    "και δεν έχεις τον κατάλληλο ρόλο για συμμετοχή στα κανάλια του event 🤔\n"
    "Θα επικοινωνήσει σύντομα μαζί σου η ομάδα {role} για να διαλευκάνει την υπόθεση!\n\n"
    "---\n\n"
    "You have already claimed a ticket! However, something weird has happened "
    "and you still don't have the necessary role to join the channels of the event 🤔\n"
    "The {role} team will contact you soon to resolve the issue! "
)

TICKET_NOT_FOUND_IN_DATABASE_MESSAGE = (
    "Το εισιτήριό σου δεν υπάρχει στη βάση μας! 😓\n"
    "Αν κάναμε λάθος, στείλε μήνυμα στην ομάδα της διοργάνωσης: {role}.\n\n"
    "---\n\n"
    "The ticket you provided does not exist! 😓\n"
    "If we made a mistake, shoot the organizers a message: {role}. "
)

TICKET_DB_ERROR_MESSAGE = (
    "Το εισιτήριό σου δεν επικυρώθηκε λόγω σφάλματος στη βάση δεδομένων. Επικοινώνησε με την ομάδα της διοργάνωσης: {role}.\n\n"
    "---\n\n"
    "The ticket was not claimed due to a database error. Please contact the organizers: {role}. "
)

TICKET_GENERIC_ERROR_MESSAGE = (
    "Δεν ξέρουμε τι ακριβώς πήγε λάθος! 😵 Επικοινώνησε με την ομάδα της διοργάνωσης: {role} για να το ψάξουν.\n\n"
    "---\n\n"
    "We have no idea what exactly went wrong! 😵 Please contact the organizers: {role} to resolve the issue. "
)

TICKET_ROLE_ASSIGNMENT_ERROR_MESSAGE = (
    "Ο ρόλος του event δε σου δόθηκε λόγω σφάλματος. Επικοινώνησε με την ομάδα της διοργάνωσης: {role}.\n\n"
    "---\n\n"
    "The attendee role was not assigned due to an error. Please contact the organizers: {role}. "
)

TICKET_ACCEPTED_MESSAGE = (
    "Ευχαριστώ που επικύρωσες το εισιτήριό σου {name}! Μπορείς να συμμετέχεις στα κανάλια της εκδήλωσης! 😊\n\n"
    "---\n\n"
    "Thank you for verifying your ticket {name}! You can now join the channels of the event! 😊 "
)

TICKET_FAILED_MESSAGE = (
    "Το εισιτήριό σου δεν επικυρώθηκε! Μπορείς να ξανααντιδράσεις με thumbs-up (👍) στο [μήνυμα για τα εισιτήρια]({link}) για να ξαναπροσπαθήσεις.\n\n"
    "---\n\n"
    "The ticket was not claimed! You can react once more with a thumbs-up (👍) to the [ticket message]({link}) to try again. "
)
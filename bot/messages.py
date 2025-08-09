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

INVALID_THREAD_MESSAGE = (
    "This command can only be used in the user's thread in the ticket channel.\n"
    "Please react to the [ticket message]({link}) if the thread is missing."
    )

TICKET_ID_MISSING_MESSAGE = (
    
    "Please provide a ticket ID."
)

INVALID_TICKET_ID_MESSAGE = (
    "Invalid ticket ID, please try again."
)

COC_NOT_ACCEPTED_MESSAGE = (
    "You have not accepted the [Code of Conduct]({link}), please react with a thumbs-up (👍) on the message."
)

TICKET_NOT_FOUND_IN_DATABASE_MESSAGE = (
    "Το εισιτήριό σου δεν υπάρχει στη βάση μας! :'(\n"
    "Αν κάναμε λάθος, στείλε μήνυμα στην ομάδα της διοργάνωσης: {role}.\n\n"
    "---\n\n"
    "The ticket you provided does not exist! :'(\n"
    "If we made a mistake, shoot the organizers a message: {role}."
)

TICKET_IN_USE_MESSAGE = (
    "Το εισιτήριό σου υπάρχει στη βάση μας! Παρ' όλ' αυτά κάποιο άλλο μέλος το έχει ήδη χρησιμοποιήσει :'(\n"
    "Θα επικοινωνήσει σύντομα μαζί σου η ομάδα {role} για να διαλευκάνει την υπόθεση!\n\n"
    "---\n\n"
    "The ticket you provided exists! However, someone else is already using it :'(\n"
    "The {role} team will contact you soon to resolve the issue! "
)

TICKET_DOUBLE_CLAIM_MESSAGE= (
    "You have already claimed this ticket."
)

TICKET_DB_ERROR_MESSAGE = (
    "The ticket was not claimed due to a database error. Please contact the organizers: {role}."
)

TICKET_ACCEPTED_MESSAGE = (
    "Ευχαριστώ που επικύρωσες το εισιτήριό σου {name}! Μπορείς να συμμετέχεις στα κανάλια της εκδήλωσης! 😊\n\n"
    "---\n\n"
    "Thank you for verifying your ticket {name}! You can now join the channels of the event! 😊 "
)

TICKET_ROLE_ASSIGNMENT_ERROR = (
    "The ticket role was not assigned due to a database error. Please contact the organizers: {role}."
)
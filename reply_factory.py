from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)
        current_question_id = -1  # Starting point for the first question

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question in the Django session.
    '''
    if current_question_id == -1:
        return True, ""  # No answer to record for the initial welcome message

    questions = PYTHON_QUESTION_LIST
    current_question = None

    for question in questions:
        if question['id'] == current_question_id:
            current_question = question
            break

    if not current_question:
        return False, "Invalid question ID."

    if answer not in current_question['options']:
        return False, "Invalid answer. Please choose one of the available options."

    if "answers" not in session:
        session["answers"] = {}
    session["answers"][current_question_id] = answer

    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    questions = PYTHON_QUESTION_LIST
    next_question = None
    next_question_id = -1

    for index, question in enumerate(questions):
        if question['id'] == current_question_id:
            if index + 1 < len(questions):
                next_question = questions[index + 1]
                next_question_id = next_question['id']
            break

    if next_question:
        return next_question['question'], next_question_id
    else:
        return None, next_question_id


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the user's answers
    for questions in the PYTHON_QUESTION_LIST.
    '''
    questions = PYTHON_QUESTION_LIST
    correct_answers = 0
    total_questions = len(questions)

    for question in questions:
        question_id = question['id']
        if "answers" in session and session["answers"].get(question_id) == question['correct_answer']:
            correct_answers += 1

    score = (correct_answers / total_questions) * 100
    return f"Quiz completed! Your score: {correct_answers}/{total_questions} ({score:.2f}%)"

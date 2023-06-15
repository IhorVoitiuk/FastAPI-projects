// Функція для автоматичного приховування повідомлення
function hideMessage() {
  // Отримання елемента повідомлення
  var message = document.getElementById("message-form");

  // Перевірка, чи існує повідомлення
  if (message) {
    // Приховування повідомлення
    message.style.display = "none";
  }
}

// Виклик функції приховування через 6 секунд
setTimeout(hideMessage, 6000);

// JavaScript to toggle visibility of feedback form
document.getElementById('toggleFeedbackForm').addEventListener('click', function () {
    var feedbackForm = document.getElementById('feedbackForm');
    if (feedbackForm.style.display === 'none' || feedbackForm.style.display === '') {
        feedbackForm.style.display = 'block';
    } else {
        feedbackForm.style.display = 'none';
    }
});
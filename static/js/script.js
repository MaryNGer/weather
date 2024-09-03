$(function() {
    $.ajax({
        url: '/static/js/cities.txt', // Путь к файлу с городами
        dataType: 'text',
        success: function(data) {
            // Разделяем содержимое файла на строки и создаем массив городов
            var availableCities = data.split('\n').map(function(city) {
                return city.trim();
            }).filter(function(city) {
                return city.length > 0;
            });

            // Используем массив городов в автокомплите
            $(".input-search").autocomplete({
                source: availableCities
            });
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var weatherSection = document.getElementById('weather');
    weatherSection.classList.add('visible');
});


//let searchBtn = document.querySelector('.search_btn');
//let searchBlock = document.querySelector('.weather-conteiner');
//// let closedBtn = document.querySelector('.search__btn-closed');
//
//searchBtn.addEventListener('click',
//    function () {
//        searchBlock.classList.toggle('weather_conteiner--active');
//    });

// closedBtn.addEventListener('click', 
// function() {
//     closedBtn.classList.toggle('search__btn-closed--active')
//     searchBlock.classList.remove('search--active')
//     body.classList.remove('stop-scroll');
// });

// let searchBtn = document.querySelector('.header__btn');
// let searchBlock = document.querySelector('.weather-conteiner');
// // let closedBtn = document.querySelector('.search__btn-closed');

// searchBtn.addEventListener('click', 
// function() {
//     // closedBtn.classList.remove('search__btn-closed--active');
//     searchBlock.classList.toggle('weather_conteiner--active');
//     // body.classList.toggle('stop-scroll');
// });

// // closedBtn.addEventListener('click', 
// // function() {
// //     closedBtn.classList.toggle('search__btn-closed--active')
// //     searchBlock.classList.remove('search--active')
// //     body.classList.remove('stop-scroll');
// // });
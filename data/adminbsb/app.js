// App related CSS
require('../css/app.scss');

console.log('JS is correctly loading !');

/* Handling app notifications (flashbags turned into notifications) */
$('#app-notifs div').each(function(){
    var type = $(this).data('type');
    var icon = '';
    if(type == 'success') icon = 'fas fa-check-circle';
    if(type == 'danger') icon = 'fas fa-exclamation-circle';
    if(type == 'info') icon = 'fas fa-info-circle';
    if(type == 'warning') icon = 'fas fa-exclamation-triangle';
    $.notify({
        icon: icon,
        message: $(this).html()
    },{
        type: $(this).data('type'),
        delay: 20000
    })
});

/* Handling pictures */
const imagesContext = require.context('../images', true, /\.(png|jpg|jpeg|gif|ico|svg|webp)$/);
imagesContext.keys().forEach(imagesContext);
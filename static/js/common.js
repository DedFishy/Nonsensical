const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

function stringDateToRelativeStringDate(date) {
    const dateObj = new Date(date);
    const currentDateObj = new Date();
    if (dateObj.getFullYear() == currentDateObj.getFullYear()) {
        if (dateObj.getMonth() == currentDateObj.getMonth()) {
            if (dateObj.getDate() == currentDateObj.getDate()) {
                if (dateObj.getHours() == currentDateObj.getHours()) {
                    if (dateObj.getMinutes() == currentDateObj.getMinutes()) {
                        return "just now";
                    } else { // Absolute minute
                        const numMinutesAgo = currentDateObj.getMinutes() - dateObj.getMinutes();
                        if (numMinutesAgo == 1) return `${numMinutesAgo} minute ago`;
                        return `${numMinutesAgo} minutes ago`;
                    }
                } else { // Absolute hour
                    const numHoursAgo = currentDateObj.getHours() - dateObj.getHours();
                    if (numHoursAgo == 1) return `${numHoursAgo} hour ago`;
                    return `${numHoursAgo} hours ago`;
                }
            } else { // Absolute day
                const numDaysAgo = currentDateObj.getDate() - dateObj.getDate();
                if (numDaysAgo == 1) return "yesterday";
                return `${numDaysAgo} days Ago`
            }
        } else { // Absolute month
            return `${months[dateObj.getMonth()]} ${dateObj.getDate()}`;
        }

    } else { // Absolute date
        return `${months[dateObj.getMonth()]} ${dateObj.getDate()}, ${dateObj.getFullYear()}`;
    }
}

const imageTypes = ["png", "jpeg", "jpg", "webp", "gif"];
const audioTypes = ["mp3", "wav"];

function getFileType(filename) {
    const filenameSplit = filename.split(".");
    return filenameSplit[filenameSplit.length-1];
}

function constructFileElement(filename, post_id) {
    const filetype = getFileType(filename);
    const url = `/postmedia/${post_id}/${filename}`;
    if (imageTypes.includes(filetype)) {
        const element = document.createElement("img");
        element.src = url;
        return element;
    } else if (audioTypes.includes(filetype)) {
        const element = document.createElement("audio");
        element.controls = true;
        const source = document.createElement("source");
        source.src = url;
        element.appendChild(source);
        return element;
    } else {
        const element = document.createElement("a");
        element.innerText = filename;
        element.href = url;
        return element;
    }
}

function escapeHTML(str){
    var p = document.createElement("p");
    p.appendChild(document.createTextNode(str));
    return p.innerHTML;
}
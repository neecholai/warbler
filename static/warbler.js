$(function () {
    $('.follow-btn').on("click", async function (e) {
        e.preventDefault()
        let user_id = +e.target.id;
        let $followButton = $(e.target);

        if ($(e.target).text() === 'Unfollow') {
            let resp = await unfollow(user_id);
            let followingCount = $followButton.closest("#all-the-way-up").find("#following-count");


            if (resp.id === user_id) {
                $followButton.text('Follow');
                $followButton.toggleClass('btn-primary btn-outline-primary');
                let updatedFollowingCount = +followingCount.text() - 1;
                followingCount.text(updatedFollowingCount);
            }
        } else {

            let resp = await follow(user_id);

            if (resp.id === user_id) {
                $followButton.text('Unfollow');
                $followButton.toggleClass('btn-outline-primary btn-primary');
                let updatedFollowingCount = +followingCount.text() + 1
                followingCount.text(updatedFollowingCount);
            }
        }
    })


    $('.fa-heart').on("click", async function (e) {
        let $heart = $(e.target);
        let msg_id = +e.target.id;
        let resp = await toggleLike(msg_id);
        let allHearts = $heart.closest('#messages').find(`.message-${msg_id}`);
        let postLikes = $heart.closest("#messages").find(`.like-count-${msg_id}`);
        let postLikesModal = $heart.closest("#messages").find(`.modal-like-count-${msg_id}`);
        let userLikes = $heart.closest('#all-the-way-up').find('#user-like-count');
        let g_username = resp.g_user_username;
        let page_username = $heart.closest("#all-the-way-up").find("#sidebar-username").text().slice(1)

        if (resp.msg_id === msg_id) {
            if ($heart.hasClass('fas')) {
                let updatedPostLikes = +postLikes.text() - 1;
                postLikes.text(updatedPostLikes);
                postLikesModal.text(updatedPostLikes);
                if (g_username === page_username) {
                    let updatedUserLikes = +userLikes.text() - 1;
                    userLikes.text(updatedUserLikes);
                }
            } else {
                let updatedPostLikes = +postLikes.text() + 1;
                postLikes.text(updatedPostLikes);
                postLikesModal.text(updatedPostLikes);
                if (g_username === page_username) {
                    let updatedUserLikes = +userLikes.text() + 1;
                    userLikes.text(updatedUserLikes);
                }
            }
            allHearts.toggleClass('fas far');
        }

    })

    $('.fa-retweet').on("click", async function (e) {
        let $retweet = $(e.target);
        let msg_id = +e.target.id;
        let resp = await toggleRetweet(msg_id);
        let allRetweets = $retweet.closest('#messages').find(`.retweet-${msg_id}`);
        let postLikes = $retweet.closest("#messages").find(`.retweet-count-${msg_id}`);
        let postLikesModal = $retweet.closest("#messages").find(`.modal-retweet-count-${msg_id}`);
        let userLikes = $retweet.closest('#all-the-way-up').find('#user-retweet-count');
        let g_username = resp.g_user_username;
        let page_username = $retweet.closest("#all-the-way-up").find("#sidebar-username").text().slice(1)

        if (resp.msg_id === msg_id) {
            if ($retweet.hasClass('retweet-green')) {
                let updatedPostLikes = +postLikes.text() - 1;
                postLikes.text(updatedPostLikes);
                postLikesModal.text(updatedPostLikes);
                if (g_username === page_username) {
                    let updatedUserLikes = +userLikes.text() - 1;
                    userLikes.text(updatedUserLikes);
                }
            } else {
                let updatedPostLikes = +postLikes.text() + 1;
                postLikes.text(updatedPostLikes);
                postLikesModal.text(updatedPostLikes);
                if (g_username === page_username) {
                    let updatedUserLikes = +userLikes.text() + 1;
                    userLikes.text(updatedUserLikes);
                }
            }
            allRetweets.toggleClass('retweet-green');
        }

    })

    $('#post-warble').on("click", async function(){
        let text = $('.new-message-modal-body').val();
        let resp = await axios.post('/messages/new', data={text})
        window.location = '/';
        return resp;
    })

    async function toggleLike(msg_id) {
        let resp = await axios.post(`/messages/${msg_id}/toggle-like`);
        return resp.data;
    }

    async function toggleRetweet(msg_id) {
        let resp = await axios.post(`/messages/${msg_id}/toggle-retweet`);
        return resp.data;
    }

    async function unfollow(user_id) {
        let resp = await axios.post(`/users/stop-following/${user_id}`);
        return resp.data;
    }

    async function follow(user_id) {
        let resp = await axios.post(`/users/follow/${user_id}`);
        return resp.data;
    }



})
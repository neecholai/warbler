$(function(){
    $('.follow-btn').on("click", async function(e) {
        e.preventDefault()
        if ($(e.target).text()==='Unfollow'){
            user_id=+e.target.id
            resp = await unfollow(user_id)

            if (resp.id===user_id){
                $(e.target).text('Follow')
                $(e.target).toggleClass('btn-primary btn-outline-primary')
                followingCount = $(e.target).closest("#all-the-way-up").find("#following-count")
                updatedFollowingCount = +followingCount.text()-1
                followingCount.text(updatedFollowingCount)
            }
        }
        
        else{
            user_id=+e.target.id
            resp = await follow(user_id)

            if (resp.id===user_id){
                $(e.target).text('Unfollow')
                $(e.target).toggleClass('btn-outline-primary btn-primary') 
                followingCount = $(e.target).closest("#all-the-way-up").find("#following-count")
                updatedFollowingCount = +followingCount.text()+1
                followingCount.text(updatedFollowingCount)
            }
        }
    })


    $('.fa-heart').on("click", async function(e) {
        msg_id=+e.target.id
        resp = await toggleLike(msg_id)
        if (resp.msg_id===msg_id){
            if ($(e.target).hasClass('fas')){
                likeCount = $(e.target).closest(".message-area").find(".like-count")
                updatedLikeCount = +likeCount.text()-1
                likeCount.text(updatedLikeCount)
            }
            else{
                likeCount = $(e.target).closest(".message-area").find(".like-count")
                updatedLikeCount = +likeCount.text()+1
                likeCount.text(updatedLikeCount)
            }
            $(e.target).toggleClass('fas far')
        }

    })

    async function toggleLike(msg_id){
        resp = await axios.post(`/messages/${msg_id}/toggle-like`)
        return resp.data
    }

    async function unfollow(user_id){
        resp = await axios.post(`/users/stop-following/${user_id}`)
        return resp.data
    }
    
    async function follow(user_id){
        resp = await axios.post(`/users/follow/${user_id}`)
        return resp.data
    }
})
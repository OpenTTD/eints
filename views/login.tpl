%rebase('main_template', title='Web Translator - Login')
<h1 class="eint-heading-icon">Login</h1>
<br />
<form action="/login" method="post" enctype="multipart/form-data">
    <input type="hidden" name="redirect" value="{{ req_redirect or "" }}"/>
    <div class="mx-auto w-50">
        <div class="mb-3">
            <label for="name">Username</label>
            <input class="form-control" type="text" id="login" name="login" value="{{ req_login or "" }}"/>
        </div>
        <div class="mb-3">
            <label for="password">Password</label>
            <input class="form-control" type="password" id="password" name="password"/>
        </div>
        <button class="btn btn-primary" type="submit" value="Login">Login</button>
    </div>
</form>

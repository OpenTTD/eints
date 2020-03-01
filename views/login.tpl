%rebase('main_template', title='Web Translator - Login')
<h1 class="eint-heading-icon">Login</h1>
<br />
<form class="form well" action="/login" method="post" enctype="multipart/form-data">
    <br />
    <fieldset style="padding-left:160px;">
        <input type="hidden" name="redirect" value="{{ req_redirect or "" }}"/>
        <label for="name">Username</label>
        <input class="input-xxlarge" type="text" id="login" name="login" value="{{ req_login or "" }}"/>
        <br />
        <label for="password">Password</label>
        <input class="input-xxlarge" type="password" id="password" name="password"/>
        <br />
        <br />
        <div class="control-group">
            <button class="btn btn-primary" type="submit" value="Login">Login</button>
        </div>
    </fieldset>
</form>

# canvas-automation
Automate repetitive tasks for grading submissions in Canvas


[clone repository](#user-content-clone-repository)  
[create virtual environment](#user-content-create-virtual-environment)  
[test2](#user-content-re-activate-virtual-environment)

# Setup:
- ##### clone repository
```
  git clone https://github.com/WillWeatherford/canvas-automation.git
```


- ##### create virtual environment
    - install [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) and [virtualenv wrapper](http://docs.python-guide.org/en/latest/dev/virtualenvs/#virtualenvwrapper-ref) if needed
    - virtualenv wrapper ()
        - mkvirtualenv <venv>
        ```
          $ mkvirtualenv grading_101d2
        ```

    - default virtual env
        - python -m virtualenviron <venv>
        ```
          $ python -m virtualenviron grading_401f3
        ```


- #### acquire API key from canvas
    - navigate to Account > Settings
    - Approved Integrations
    - 'New Access Token'
    - add description (e.g. grading_201d3) and expiration date (course ending date?)
    - generate token
    - copy token to clipboard
    - DO NOT close window until you have added token to virtualenv activate script as token is not visible after closing window


- #### add "API\_TOKEN" and "COURSE\_ID" to virtual environment activate script
    - open virtualenv activate script
        - sublime:
        ```
          $ subl ~/.virtualenvs/<venv>/bin/activate
        ```
        - atom:
        ```
          $ atom ~/.virtualenvs/<venv>/bin/activate
        ```

        - if not using virtualenv wrapper:
        ```
          $ sublime <venv>/bin/activate
        ```
        or
        ```
          $ atom <venv>/bin/activate
        ```

    - add API_TOKEN and COURSE_ID environment variables to activate
    ```
      EXPORT API_TOKEN=""
      EXPORT COURSE_ID=""
    ```


- #### re-activate virtual environment
    - deactivate environment
    ```
      $ deactivate
    ```

    - activate environment:

      - if using virtualenv wrapper:
      ```
        $ workon <virtual env>
      ```

      - if using virtualenv:
      ```
        $ source bin/activate
      ```


- #### run auto_canvas
    ```
  $ python auto_canvas.py
    ```

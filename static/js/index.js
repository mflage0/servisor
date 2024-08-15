new Vue({
    el: '#app',
    data: {
        status: null,
        version: null,
        items: null,
        loading: true,
        dialogVisible: false,
        input: '',
        activeName: 'first',
        tabVisible: false,
        makeVisible: false,
        input_read: false,
        title: '编辑',
        edit_name: '',

        ruleForm: {
            name: '',
            command: '',
            directory: '',
        },
        rules: {
            name: [
                { required: true, message: '请输入请填写必填项', trigger: 'blur' },
                { min: 3, max: 15, message: '长度在 3 到 15 个字符', trigger: 'blur' }
            ],
            command: [
                { required: true, message: '请输入请填写必填项', trigger: 'blur' }
            ],
            directory: [
                { required: true, message: '请输入请填写必填项', trigger: 'blur' }
            ],
        },
        setOryw: false

    },
    created() {
        this.info()
    },
    methods: {
        submitYw() {
            this.setOryw ? this.post_setting() : this.post_process_setting()
        },
        createJc() {
            this.title = '创建'
            this.makeVisible = true;
            this.ruleForm = {
                name: '',
                command: '',
                directory: ''
            }
        },
        info() {
            axios.get(window.location.origin + '/api/v1/info', {
                withCredentials: true
            })
                .then(response => {
                    this.loading = false
                    this.$message.success('success')
                    this.status = response.data['supervisor_status'];
                    this.version = response.data['supervisor_version'];
                    this.items = response.data['data'];
                })
                .catch(function (error) {
                    this.loading = false
                    this.$message.success(error.message)
                    console.log(error);
                });
        },
        async stop() {
            try {
                this.loading = true;  // 显示蒙版
                // 第一个请求：停止操作
                await axios.get(window.location.origin + '/api/v1/stop', {
                    withCredentials: true
                });

                this.info()

            } catch (error) {
                console.log(error);
                this.$message.error(error.message)
                this.loading = false
            } finally {

            }
        },
        async restart() {
            try {
                this.loading = true;  // 显示蒙版

                // 第一个请求：重启操作
                let res = await axios.get(window.location.origin + '/api/v1/restart', {
                    withCredentials: true
                });
                console.log(res, '查看重启响应');


                // 暂停3秒
                await new Promise(resolve => setTimeout(resolve, 3000));

                this.info()

            } catch (error) {
                console.log(error);
                this.$message.error(error.message)
                this.loading = false
            } finally {

            }
        },
        async get_setting() {
            try {
                this.input_read = false
                this.setOryw = true
                let setting = await axios.get(window.location.origin + '/api/v1/setting', {
                    withCredentials: true
                });
                this.input = setting.data;
                this.dialogVisible = true;
            } catch (error) {
                console.log(error);
                this.$message.error(error.message)
                this.loading = false
            } finally {

            }

        },
        async get_process_config(name) {
            this.edit_name = name
            try {
                let setting = await axios.get(window.location.origin + '/api/v1/process/' + name, {
                    withCredentials: true
                });
                this.input = setting.data;
                this.setOryw = false
                this.dialogVisible = true;
            } catch (error) {
                console.log(error);
                this.$message.error(error.message)
                this.loading = false
            } finally {

            }
        },
        async edit_process_config(item) {
            this.title = '编辑'
            this.ruleForm = JSON.parse(JSON.stringify(item))
            this.makeVisible = true
        },
        async get_process_log(name) {
            this.input_read = true
            this.now_name = name
            this.get_process_log_out(name)
        },
        async get_process_log_out() {
            try {
                let setting = await axios.get(window.location.origin + '/api/v1/log/' + this.now_name + '/out', {
                    withCredentials: true
                });
                this.input = setting.data;
                this.tabVisible = true;
            } catch (error) {
                console.log(error);
                this.$message.error(error.message)
                this.loading = false
            } finally {

            }
        },
        async get_process_log_err() {
            try {
                let setting = await axios.get(window.location.origin + '/api/v1/log/' + this.now_name + '/err', {
                    withCredentials: true
                });
                this.input = setting.data;
            } catch (error) {
                console.log(error);
                this.$message.error(error.message)
                this.loading = false
            } finally {

            }
        },
        async stop_process(name) {
            try {
                this.loading = true;
                let body = {
                    "name": name,
                    "operate": "stop"
                }
                await axios.post(window.location.origin + '/api/v1/process', body, {
                    withCredentials: true
                });
                this.info()
            } catch (error) {
                console.log(error);
                this.$message.error(error.message)
                this.loading = false
            } finally {

            }
        },
        async start_process(name) {
            try {
                this.loading = true;
                let body = {
                    "name": name,
                    "operate": "start"
                }
                await axios.post(window.location.origin + '/api/v1/process', body, {
                    withCredentials: true
                });
                this.info()
            } catch (error) {
                console.log(error);
                this.$message.error(error.message)
                this.loading = false
            } finally {

            }
        },
        async restart_process(name) {
            try {
                this.loading = true;
                let body = {
                    "name": name,
                    "operate": "restart"
                }
                await axios.post(window.location.origin + '/api/v1/process', body, {
                    withCredentials: true
                });
                this.info()
            } catch (error) {
                console.log(error);
                this.$message.error(error.message)
                this.loading = false
            } finally {

            }
        },
        async delete_process(name) {
            try {
                this.loading = true;  // 显示蒙版
                let url = window.location.origin + '/api/v1/process/' + name
                await axios.delete(url, {
                    withCredentials: true
                });
                await new Promise(resolve => setTimeout(resolve, 3000));
                this.info()
            } catch (error) {
                console.log(error);
                this.$message.error(error.message)
                this.loading = false
            } finally {

            }
        },
        async make_process(name, directory, command) {
            try {
                this.loading = true;  // 显示蒙版
                let url = window.location.origin + '/api/v1/process/' + name
                let body = {
                    "directory": directory,
                    "command": command
                }
                await axios.post(url, body, {
                    withCredentials: true
                });
                await new Promise(resolve => setTimeout(resolve, 3000));
                this.info()
            } catch (error) {
                console.log(error);
                this.$message.error(error.message)
                this.loading = false
            } finally {

            }
        },
        async post_setting() {
            try {
                this.dialogVisible = false;
                this.loading = true;  // 显示蒙版
                let url = window.location.origin + '/api/v1/setting'
                let body = {
                    "setting_config": this.input
                }
                await axios.put(url, body, {
                    withCredentials: true
                });
                await new Promise(resolve => setTimeout(resolve, 3000));
                this.info()
            } catch (error) {
                console.log(error);
                this.$message.error(error.message)
                this.loading = false
            } finally {

            }
        },
        async post_process_setting() {
            try {
                this.dialogVisible = false;
                this.loading = true;  // 显示蒙版
                let url = window.location.origin + '/api/v1/process/' + this.edit_name
                let body = {
                    "process_config": this.input
                }
                await axios.put(url, body, {
                    withCredentials: true
                });
                await new Promise(resolve => setTimeout(resolve, 3000));
                this.info()
            } catch (error) {
                console.log(error);
                this.$message.error(error.message)
                this.loading = false
            } finally {
            }
        },
        handleClose(done) {
            this.dialogVisible = false
            this.tabVisible = false
            this.makeVisible = false
            this.input_read = true
            done()
        },
        handleClick(tab, event) {
            console.log(tab, event);
            if (tab.name === 'first') {
                this.input_read = true
                this.get_process_log_out()
            } else {
                this.get_process_log_err()
                this.input_read = true
            }
        },
        submitForm(formName) {
            this.$refs[formName].validate((valid) => {
                if (valid) {
                    console.log(this.ruleForm);
                    this.make_process(this.ruleForm.name, this.ruleForm.directory, this.ruleForm.command)
                    this.makeVisible = false
                } else {
                    console.log('error submit!!');
                    return false;
                }
            });
        },
        resetForm(formName) {
            this.makeVisible = false
            this.$refs[formName].resetFields();
        }
    }
})